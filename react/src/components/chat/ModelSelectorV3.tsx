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
          <div>{t('chat:modelSelector.title')}</div>
        </div>
        <ScrollArea>
          <div className="max-h-80 h-80 px-4 pb-4 select-none">
            {/* 文本模型部分 */}
            <div className="mb-4">
              <div className="text-sm font-medium text-muted-foreground mb-2">文本模型</div>
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

            {/* 工具模型部分 */}
            {Object.keys(groupedTools).length > 0 && (
              <div>
                <div className="text-sm font-medium text-muted-foreground mb-2">圖像/視頻模型</div>
                {Object.entries(groupedTools).map(([provider, providerTools], index, array) => {
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
                      {providerTools.map((tool: any) => {
                        const toolKey = tool.provider + ':' + tool.id
                        const isToolSelected = selectedToolKeys.includes(toolKey)

                        return (
                          <div
                            key={toolKey}
                            className="flex items-center justify-between p-3 hover:bg-muted/50 transition-colors mb-2 cursor-pointer"
                            onClick={() => handleToolToggle(toolKey, !isToolSelected)}
                          >
                            <div className="flex-1">
                              <div className="font-medium text-sm">
                                {tool.type === 'video' ? '🎬 ' : '🎨 '}
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
                      {!isLastGroup && <DropdownMenuSeparator className="my-2" />}
                    </DropdownMenuGroup>
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
