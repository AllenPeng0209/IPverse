import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'motion/react'
import { getTopIPs, recordIPInteraction, type IP } from '@/api/ip'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Heart, Eye, TrendingUp, Sparkles } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { toast } from 'sonner'

interface IPRankingProps {
  className?: string
}

const IPRanking: React.FC<IPRankingProps> = ({ className = '' }) => {
  const { t } = useTranslation()
  const [selectedIP, setSelectedIP] = useState<IP | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const { data: topIPs = [], isLoading } = useQuery({
    queryKey: ['topIPs'],
    queryFn: () => getTopIPs(8),
  })

  const handleIPClick = async (ip: IP) => {
    setSelectedIP(ip)
    setIsDialogOpen(true)
    
    // 记录浏览交互
    try {
      await recordIPInteraction(ip.id, { interaction_type: 'view' })
    } catch (error) {
      console.warn('Failed to record view interaction:', error)
    }
  }

  const handleLike = async (ip: IP, event: React.MouseEvent) => {
    event.stopPropagation()
    
    try {
      await recordIPInteraction(ip.id, { interaction_type: 'like' })
      toast.success(`已点赞 ${ip.name}！`)
    } catch (error) {
      toast.error('点赞失败，请稍后重试')
      console.error('Failed to record like interaction:', error)
    }
  }

  const getRankIcon = (index: number) => {
    if (index === 0) return <span className="text-yellow-500 text-xl">🏆</span>
    if (index === 1) return <span className="text-gray-400 text-xl">🥈</span>
    if (index === 2) return <span className="text-amber-600 text-xl">🥉</span>
    return <span className="text-gray-600 font-bold">#{index + 1}</span>
  }

  if (isLoading) {
    return (
      <div className={`flex flex-col px-10 mt-16 gap-4 select-none max-w-[1200px] mx-auto ${className}`}>
        <div className="text-2xl font-bold text-center mb-6">
          <div className="w-48 h-8 bg-gray-200 rounded animate-pulse mx-auto"></div>
        </div>
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-gray-100 rounded-lg h-80 animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <>
      <div className={`flex flex-col px-10 mt-16 gap-4 select-none max-w-[1200px] mx-auto ${className}`}>
        <motion.div
          className="text-center mb-6"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl font-bold flex items-center justify-center gap-2 mb-2">
            <TrendingUp className="text-red-500" />
            IP 热度排行榜
            <Sparkles className="text-yellow-500" />
          </h2>
          <p className="text-gray-600">发现最受欢迎的虚拟角色</p>
        </motion.div>

        <AnimatePresence>
          <div className="grid grid-cols-4 gap-4 w-full pb-10">
            {topIPs.map((ip, index) => (
              <motion.div
                key={ip.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ scale: 1.02, y: -5 }}
                className="cursor-pointer"
                onClick={() => handleIPClick(ip)}
              >
                <Card className="h-full overflow-hidden border-2 hover:border-primary/50 transition-all duration-300 hover:shadow-lg">
                  <div className="relative">
                    {/* 排名徽章 */}
                    <div className="absolute top-2 left-2 z-10 bg-white/90 backdrop-blur-sm rounded-full p-2 shadow">
                      {getRankIcon(index)}
                    </div>
                    
                    {/* 热度分数 */}
                    <div className="absolute top-2 right-2 z-10 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold">
                      🔥 {ip.heat_score}
                    </div>

                    {/* IP图片 */}
                    <div className="w-full h-48 overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200">
                      <img
                        src={ip.image_url}
                        alt={ip.name}
                        className="w-full h-full object-cover hover:scale-110 transition-transform duration-500"
                        onError={(e) => {
                          e.currentTarget.src = `https://via.placeholder.com/300x400/6366f1/ffffff?text=${encodeURIComponent(ip.name)}`
                        }}
                      />
                    </div>
                  </div>

                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-bold text-lg truncate">{ip.name}</h3>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-500 hover:text-red-600 hover:bg-red-50"
                        onClick={(e) => handleLike(ip, e)}
                      >
                        <Heart className="w-4 h-4" />
                        <span className="ml-1 text-xs">{ip.like_count}</span>
                      </Button>
                    </div>

                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {ip.description}
                    </p>

                    {/* 分类标签 */}
                    {ip.category_name && (
                      <Badge variant="secondary" className="text-xs mb-2">
                        {ip.category_name}
                      </Badge>
                    )}

                    {/* 统计信息 */}
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <div className="flex items-center gap-1">
                        <Eye className="w-3 h-3" />
                        <span>{ip.view_count.toLocaleString()}</span>
                      </div>
                      <div className="flex gap-1">
                        {ip.tags?.slice(0, 2).map((tag, i) => (
                          <span key={i} className="bg-gray-100 px-2 py-1 rounded text-xs">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </AnimatePresence>
      </div>

      {/* IP详情对话框 */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedIP && getRankIcon(topIPs.findIndex(ip => ip.id === selectedIP.id))}
              {selectedIP?.name}
            </DialogTitle>
          </DialogHeader>
          
          {selectedIP && (
            <ScrollArea className="max-h-[60vh]">
              <div className="space-y-4">
                {/* IP图片 */}
                <div className="w-full h-64 overflow-hidden rounded-lg bg-gradient-to-br from-gray-100 to-gray-200">
                  <img
                    src={selectedIP.image_url}
                    alt={selectedIP.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.src = `https://via.placeholder.com/400x300/6366f1/ffffff?text=${encodeURIComponent(selectedIP.name)}`
                    }}
                  />
                </div>

                {/* 基本信息 */}
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="bg-red-50 p-3 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">{selectedIP.heat_score}</div>
                    <div className="text-sm text-gray-600">热度分数</div>
                  </div>
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{selectedIP.view_count.toLocaleString()}</div>
                    <div className="text-sm text-gray-600">浏览次数</div>
                  </div>
                  <div className="bg-pink-50 p-3 rounded-lg">
                    <div className="text-2xl font-bold text-pink-600">{selectedIP.like_count.toLocaleString()}</div>
                    <div className="text-sm text-gray-600">点赞数</div>
                  </div>
                </div>

                {/* 分类和标签 */}
                <div className="space-y-2">
                  {selectedIP.category_name && (
                    <div>
                      <span className="text-sm font-medium text-gray-700">分类：</span>
                      <Badge variant="outline" className="ml-2">{selectedIP.category_name}</Badge>
                    </div>
                  )}
                  
                  {selectedIP.tags && selectedIP.tags.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-gray-700">标签：</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {selectedIP.tags.map((tag, i) => (
                          <Badge key={i} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* IP描述 */}
                <div>
                  <h4 className="font-medium mb-2">角色介绍</h4>
                  <p className="text-gray-700 leading-relaxed">{selectedIP.description}</p>
                </div>

                {/* 交互按钮 */}
                <div className="flex gap-2 pt-4">
                  <Button
                    onClick={() => handleLike(selectedIP, {} as React.MouseEvent)}
                    className="flex-1"
                    variant="outline"
                  >
                    <Heart className="w-4 h-4 mr-2" />
                    点赞
                  </Button>
                  <Button
                    onClick={() => {
                      recordIPInteraction(selectedIP.id, { interaction_type: 'share' })
                      toast.success('已分享到剪贴板！')
                      navigator.clipboard.writeText(`快来看看这个超棒的IP角色：${selectedIP.name}`)
                    }}
                    className="flex-1"
                    variant="outline"
                  >
                    分享
                  </Button>
                </div>
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}

export default IPRanking