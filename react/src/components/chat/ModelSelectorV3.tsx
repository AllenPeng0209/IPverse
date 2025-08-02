import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { ChevronDown } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuGroup,
} from '@/components/ui/dropdown-menu'
import { Checkbox } from '@/components/ui/checkbox'
import { useTranslation } from 'react-i18next'
import { useConfigs } from '@/contexts/configs'
import { Model } from '@/types/types'
import { PROVIDER_NAME_MAPPING } from '@/constants'
import { ScrollArea } from '@/components/ui/scroll-area'

interface ModelSelectorV3Props {
  onModelToggle?: (modelId: string, checked: boolean) => void
}

const ModelSelectorV3: React.FC<ModelSelectorV3Props> = ({
  onModelToggle,
}) => {
  const {
    textModel,
    setTextModel,
    textModels,
    selectedTools,
    setSelectedTools,
    allTools,
  } = useConfigs()

  // 調試信息
  console.log('🎨 ModelSelectorV3 Debug:', {
    allToolsLength: allTools?.length || 0,
    selectedToolsLength: selectedTools?.length || 0,
    textModelsLength: textModels?.length || 0
  })

  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'text' | 'image' | 'video'>('text')
  const { t } = useTranslation()

  const groupLLMsByProvider = (models: Model[]) => {
    const grouped: { [provider: string]: Model[] } = {}
    models?.forEach((model) => {
      if (!grouped[model.provider]) {
        grouped[model.provider] = []
      }
      grouped[model.provider].push(model)
    })
    return grouped
  }

  const sortProviders = <T,>(grouped: { [provider: string]: T[] }) => {
    const sortedEntries = Object.entries(grouped).sort(([a], [b]) => {
      if (a === 'jaaz') return -1
      if (b === 'jaaz') return 1
      return a.localeCompare(b)
    })
    return Object.fromEntries(sortedEntries)
  }

  const groupedLLMs = sortProviders(groupLLMsByProvider(textModels))

  // 工具分組邏輯
  const groupToolsByProvider = (tools: any[]) => {
    const grouped: { [provider: string]: any[] } = {}
    tools?.forEach((tool) => {
      const provider = tool.provider || 'unknown'
      if (!grouped[provider]) {
        grouped[provider] = []
      }
      grouped[provider].push(tool)
    })
    return grouped
  }

  const groupedTools = sortProviders(groupToolsByProvider(allTools))
  const selectedToolKeys = selectedTools.map(
    (tool) => tool.provider + ':' + tool.id
  )

  // 按類型分組工具
  const imageTools = allTools.filter(tool => tool.type === 'image')
  const videoTools = allTools.filter(tool => tool.type === 'video')
  const groupedImageTools = sortProviders(groupToolsByProvider(imageTools))
  const groupedVideoTools = sortProviders(groupToolsByProvider(videoTools))

  const handleModelClick = (modelKey: string) => {
    const model = textModels?.find((m) => m.provider + ':' + m.model === modelKey)
    if (model) {
      setTextModel(model)
      localStorage.setItem('text_model', modelKey)
      onModelToggle?.(modelKey, true)
    }
  }

  const isModelSelected = (modelKey: string) => {
    return textModel?.provider + ':' + textModel?.model === modelKey
  }

  // 工具選擇處理
  const handleToolToggle = (toolKey: string, checked: boolean) => {
    const tool = allTools.find((t) => t.provider + ':' + t.id === toolKey)
    if (!tool) return

    let newSelected: any[] = []
    if (checked) {
      newSelected = [...selectedTools, tool]
    } else {
      newSelected = selectedTools.filter(
        (t) => t.provider + ':' + t.id !== toolKey
      )
    }

    setSelectedTools(newSelected)
    localStorage.setItem(
      'disabled_tool_ids',
      JSON.stringify(
        allTools.filter((t) => !newSelected.includes(t)).map((t) => t.id)
      )
    )
  }

  const getProviderDisplayInfo = (provider: string) => {
    const providerInfo = PROVIDER_NAME_MAPPING[provider]
    return {
      name: providerInfo?.name || provider,
      icon: providerInfo?.icon,
    }
  }

  return (
    <DropdownMenu open={dropdownOpen} onOpenChange={setDropdownOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          size={'sm'}
          variant="outline"
          className="w-fit max-w-[40%] justify-between overflow-hidden"
        >
          <span>{textModel?.model || t('chat:modelSelector.selectModel')}</span>
          <ChevronDown className="ml-2 h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-96 select-none">
        <div className="flex items-center justify-between px-4 py-2 border-b">
          <div>Model</div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Auto</span>
            <div className="w-8 h-4 bg-white rounded-full border flex items-center justify-end px-0.5">
              <div className="w-3 h-3 bg-black rounded-full"></div>
            </div>
          </div>
        </div>

        {/* 標籤頁 */}
        <div className="flex px-4 py-2 gap-1">
          <button
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'image'
              ? 'bg-white text-black border-2 border-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            onClick={() => setActiveTab('image')}
          >
            Image
          </button>
          <button
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'video'
              ? 'bg-white text-black border-2 border-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            onClick={() => setActiveTab('video')}
          >
            Video
          </button>
          <button
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'text'
              ? 'bg-white text-black border-2 border-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            onClick={() => setActiveTab('text')}
          >
            Text
          </button>
        </div>

        <ScrollArea>
          <div className="max-h-80 h-80 px-4 pb-4 select-none">
            {/* 文本模型標籤頁 */}
            {activeTab === 'text' && (
              <div>
                {Object.entries(groupedLLMs).map(([provider, providerModels], index, array) => {
                  const providerInfo = getProviderDisplayInfo(provider)
                  const isLastGroup = index === array.length - 1
                  return (
                    <DropdownMenuGroup key={provider}>
                      <DropdownMenuLabel className="text-xs font-medium text-muted-foreground px-0 py-2">
                        <div className="flex items-center gap-2">
                          <img
                            src={providerInfo.icon}
                            alt={providerInfo.name}
                            className="w-4 h-4 rounded-full"
                          />
                          {providerInfo.name}
                        </div>
                      </DropdownMenuLabel>
                      {providerModels.map((model: Model) => {
                        const modelKey = model.provider + ':' + model.model
                        const modelName = model.model

                        return (
                          <div
                            key={modelKey}
                            className="flex items-center justify-between p-3 hover:bg-muted/50 transition-colors mb-2 cursor-pointer"
                            onClick={() => handleModelClick(modelKey)}
                          >
                            <div className="flex-1">
                              <div className="font-medium text-sm">{modelName}</div>
                            </div>
                            <Checkbox
                              checked={isModelSelected(modelKey)}
                              className="ml-4"
                            />
                          </div>
                        )
                      })}
                      {!isLastGroup && <DropdownMenuSeparator className="my-2" />}
                    </DropdownMenuGroup>
                  )
                })}
              </div>
            )}

            {/* 圖像模型標籤頁 */}
            {activeTab === 'image' && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <img src="/api/placeholder/16/16" alt="Jaaz" className="w-4 h-4 rounded-full" />
                  <span className="text-sm text-muted-foreground">Jaaz</span>
                </div>
                {Object.entries(groupedImageTools).map(([provider, providerTools], index, array) => {
                  const isLastGroup = index === array.length - 1
                  return (
                    <div key={provider}>
                      {providerTools.map((tool: any) => {
                        const toolKey = tool.provider + ':' + tool.id
                        const isToolSelected = selectedToolKeys.includes(toolKey)

                        return (
                          <div
                            key={toolKey}
                            className="flex items-center justify-between p-3 hover:bg-muted/50 transition-colors mb-2 cursor-pointer rounded-lg"
                            onClick={() => handleToolToggle(toolKey, !isToolSelected)}
                          >
                            <div className="flex-1">
                              <div className="font-medium text-sm text-white">
                                {tool.display_name || tool.id}
                              </div>
                            </div>
                            <Checkbox
                              checked={isToolSelected}
                              className="ml-4"
                            />
                          </div>
                        )
                      })}
                      {!isLastGroup && <div className="my-2" />}
                    </div>
                  )
                })}
              </div>
            )}

            {/* 視頻模型標籤頁 */}
            {activeTab === 'video' && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <img src="/api/placeholder/16/16" alt="Jaaz" className="w-4 h-4 rounded-full" />
                  <span className="text-sm text-muted-foreground">Jaaz</span>
                </div>
                {Object.entries(groupedVideoTools).map(([provider, providerTools], index, array) => {
                  const isLastGroup = index === array.length - 1
                  return (
                    <div key={provider}>
                      {providerTools.map((tool: any) => {
                        const toolKey = tool.provider + ':' + tool.id
                        const isToolSelected = selectedToolKeys.includes(toolKey)

                        return (
                          <div
                            key={toolKey}
                            className="flex items-center justify-between p-3 hover:bg-muted/50 transition-colors mb-2 cursor-pointer rounded-lg"
                            onClick={() => handleToolToggle(toolKey, !isToolSelected)}
                          >
                            <div className="flex-1">
                              <div className="font-medium text-sm text-white">
                                {tool.display_name || tool.id}
                              </div>
                            </div>
                            <Checkbox
                              checked={isToolSelected}
                              className="ml-4"
                            />
                          </div>
                        )
                      })}
                      {!isLastGroup && <div className="my-2" />}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </ScrollArea>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default ModelSelectorV3
