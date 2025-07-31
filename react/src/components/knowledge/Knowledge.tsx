import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { toast } from 'sonner'
import { Card, CardContent, CardHeader } from '../ui/card'
import { getKnowledgeList } from '@/api/knowledge'
import TopMenu from '../TopMenu'

export default function Knowledge() {
  const { t } = useTranslation()
  const [knowledgeList, setKnowledgeList] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  // Fetch knowledge list
  const fetchKnowledgeList = async () => {
    try {
      setLoading(true)
      const response = await getKnowledgeList()
      setKnowledgeList(response)
    } catch (error) {
      console.error('Failed to fetch knowledge list:', error)
      toast.error('获取知识库列表失败')
      setKnowledgeList([])
    } finally {
      setLoading(false)
    }
  }

  // Initial load
  useEffect(() => {
    fetchKnowledgeList()
  }, [])

  return (
    <div>
      <TopMenu />
      <div className="flex flex-col px-6">
        <h1 className="text-2xl font-bold mb-4">知识库</h1>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-8 text-muted-foreground">
            加载中...
          </div>
        )}

        {/* Empty State */}
        {!loading && knowledgeList.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            暂无知识库
          </div>
        )}

        {/* Knowledge Grid */}
        {!loading && knowledgeList.length > 0 && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
              gap: '16px',
              marginBottom: '24px',
            }}
          >
            {knowledgeList.map((knowledgeName) => {
              return (
                <Card
                  key={knowledgeName}
                  className="relative cursor-pointer hover:shadow-md transition-shadow overflow-hidden"
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <h3
                        className="text-lg font-semibold truncate flex-1 mr-2"
                      >
                        {knowledgeName}
                      </h3>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm text-muted-foreground">
                      File
                    </p>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
