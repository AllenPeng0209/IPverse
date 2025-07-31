import { getPlatformModels } from '@/api/model'
import useConfigsStore from '@/stores/configs'
import { Model } from '@/types/types'
import { useQuery } from '@tanstack/react-query'
import { createContext, useContext, useEffect } from 'react'

export const ConfigsContext = createContext<{
  configsStore: typeof useConfigsStore
  refreshModels: () => void
} | null>(null)

export const ConfigsProvider = ({
  children,
}: {
  children: React.ReactNode
}) => {
  const configsStore = useConfigsStore()
  const {
    setTextModels,
    setTextModel,
    setShowLoginDialog,
  } = configsStore

  const { data: modelList, refetch: refreshModels } = useQuery({
    queryKey: ['list_models_2'],
    queryFn: getPlatformModels,
    staleTime: 1000 * 60 * 5, // 5分钟内数据被认为是新鲜的
    placeholderData: (previousData) => previousData, // 关键：显示旧数据同时获取新数据
    refetchOnWindowFocus: true, // 窗口获得焦点时重新获取
    refetchOnReconnect: true, // 网络重连时重新获取
    refetchOnMount: true, // 挂载时重新获取
  })

  useEffect(() => {
    if (!modelList) return
    const llmModels: Model[] = Array.isArray(modelList) ? modelList : []

    setTextModels(llmModels)

    // 设置选择的文本模型
    const textModel = localStorage.getItem('text_model')
    if (
      textModel &&
      llmModels.find((m: Model) => m.provider + ':' + m.model === textModel)
    ) {
      setTextModel(
        llmModels.find((m: Model) => m.provider + ':' + m.model === textModel)
      )
    } else {
      setTextModel(llmModels.find((m: any) => (m as any).type === 'text'))
    }

    // 如果文本模型为空，则显示登录对话框
    if (llmModels.length === 0) {
      setShowLoginDialog(true)
    }
  }, [
    modelList,
    setTextModel,
    setTextModels,
    setShowLoginDialog,
  ])

  return (
    <ConfigsContext.Provider
      value={{ configsStore: useConfigsStore, refreshModels }}
    >
      {children}
    </ConfigsContext.Provider>
  )
}

export const useConfigs = () => {
  const context = useContext(ConfigsContext)
  if (!context) {
    throw new Error('useConfigs must be used within a ConfigsProvider')
  }
  return context.configsStore()
}

export const useRefreshModels = () => {
  const context = useContext(ConfigsContext)
  if (!context) {
    throw new Error('useRefreshModels must be used within a ConfigsProvider')
  }
  return context.refreshModels
}
