import { getPlatformModels, getPlatformTools } from '@/api/model'
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
    setAllTools,
    setSelectedTools,
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

  const { data: toolsList, error: toolsError, isLoading: toolsLoading } = useQuery({
    queryKey: ['list_tools'],
    queryFn: getPlatformTools,
    staleTime: 0, // 強制每次都重新獲取
    placeholderData: (previousData) => previousData,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    refetchOnMount: true,
  })

  // 調試信息
  useEffect(() => {
    console.log('🔧 Tools Query Debug:', {
      toolsList,
      toolsError,
      toolsLoading,
      toolsListLength: toolsList?.length || 0
    })
  }, [toolsList, toolsError, toolsLoading])

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

  useEffect(() => {
    if (!toolsList) return
    const tools = Array.isArray(toolsList) ? toolsList : []

    console.log('🛠️ Setting allTools:', tools)
    setAllTools(tools)

    // 设置默认选择的工具（从本地存储恢复或选择默认工具）
    const disabledToolIds = JSON.parse(localStorage.getItem('disabled_tool_ids') || '[]')
    const enabledTools = tools.filter(tool => !disabledToolIds.includes(tool.id))

    // 如果没有已选择的工具，默认选择一些图像生成工具
    if (enabledTools.length === 0 && tools.length > 0) {
      const defaultImageTools = tools.filter(tool =>
        tool.type === 'image' &&
        (tool.id.includes('flux') || tool.id.includes('midjourney') || tool.id.includes('gpt_image'))
      ).slice(0, 2) // 选择前2个默认工具
      setSelectedTools(defaultImageTools)
    } else {
      setSelectedTools(enabledTools)
    }
  }, [
    toolsList,
    setAllTools,
    setSelectedTools,
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
