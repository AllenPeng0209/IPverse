import { LLMConfig, Model } from '@/types/types'
import { ToolInfo } from '@/api/model'
import { create } from 'zustand'

type ConfigsStore = {
  initCanvas: boolean
  setInitCanvas: (initCanvas: boolean) => void

  textModels: Model[]
  setTextModels: (models: Model[]) => void

  textModel?: Model
  setTextModel: (model?: Model) => void

  selectedTools: ToolInfo[]
  setSelectedTools: (tools: ToolInfo[]) => void

  allTools: ToolInfo[]
  setAllTools: (tools: ToolInfo[]) => void

  showInstallDialog: boolean
  setShowInstallDialog: (show: boolean) => void

  showUpdateDialog: boolean
  setShowUpdateDialog: (show: boolean) => void

  showSettingsDialog: boolean
  setShowSettingsDialog: (show: boolean) => void

  showLoginDialog: boolean
  setShowLoginDialog: (show: boolean) => void

  providers: {
    [key: string]: LLMConfig
  }
  setProviders: (providers: { [key: string]: LLMConfig }) => void
}

const useConfigsStore = create<ConfigsStore>((set) => ({
  initCanvas: false,
  setInitCanvas: (initCanvas) => set({ initCanvas }),

  textModels: [],
  setTextModels: (models) => set({ textModels: models }),

  textModel: undefined,
  setTextModel: (model) => set({ textModel: model }),

  selectedTools: [],
  setSelectedTools: (tools) => set({ selectedTools: tools }),

  allTools: [],
  setAllTools: (tools) => set({ allTools: tools }),

  showInstallDialog: false,
  setShowInstallDialog: (show) => set({ showInstallDialog: show }),

  showUpdateDialog: false,
  setShowUpdateDialog: (show) => set({ showUpdateDialog: show }),

  showSettingsDialog: false,
  setShowSettingsDialog: (show) => set({ showSettingsDialog: show }),

  showLoginDialog: false,
  setShowLoginDialog: (show) => set({ showLoginDialog: show }),

  providers: {},
  setProviders: (providers) => set({ providers }),
}))

export default useConfigsStore
