"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { FileText, Download, Eye, Calendar, HardDrive, Target } from "lucide-react"
import type { SearchResult } from "@/lib/search"

interface SearchResultsProps {
  results: SearchResult[]
}

export function SearchResults({ results }: SearchResultsProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "indexed":
        return "bg-green-100 text-green-800 hover:bg-green-100"
      case "pending":
        return "bg-yellow-100 text-yellow-800 hover:bg-yellow-100"
      case "error":
        return "bg-red-100 text-red-800 hover:bg-red-100"
      case "processing":
        return "bg-blue-100 text-blue-800 hover:bg-blue-100"
      default:
        return "bg-gray-100 text-gray-800 hover:bg-gray-100"
    }
  }

  return (
    <div className="space-y-4">
      {results.map((result) => (
        <Card key={result.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <FileText className="h-5 w-5 text-muted-foreground mt-1 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-lg mb-2 truncate">{result.fileName}</h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <span className="font-medium">Client:</span>
                      <span>{result.clientName}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <span className="font-medium">Account:</span>
                      <span>{result.accountNumber}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <span className="font-medium">Department:</span>
                      <span>{result.department}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDate(result.fundDate)}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 mb-4">
                    <Badge variant="outline" className="text-xs">
                      {result.fileExtension.toUpperCase()}
                    </Badge>
                    <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                      <HardDrive className="h-3 w-3" />
                      <span>{formatFileSize(result.fileSize)}</span>
                    </div>
                    <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                      <Target className="h-3 w-3" />
                      <span>OCR: {result.ocrConfidence}%</span>
                    </div>
                    <Badge className={getStatusColor(result.indexStatus)}>{result.indexStatus}</Badge>
                  </div>

                  <div className="text-sm text-muted-foreground">
                    <span className="font-medium">Modified:</span> {formatDate(result.dateModified)}
                  </div>

                  {result.snippet && (
                    <div className="mt-3 p-3 bg-muted/50 rounded-md">
                      <p className="text-sm text-muted-foreground">
                        <span className="font-medium">Preview:</span> {result.snippet}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2 ml-4">
                <Button variant="outline" size="sm">
                  <Eye className="h-4 w-4 mr-1" />
                  View
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-1" />
                  Download
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
