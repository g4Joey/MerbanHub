"use client"

import { FileUpload } from "@/components/file-upload"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  const handleFilesSelected = (files: File[]) => {
    console.log("Files selected:", files)
  }

  const handleFileRemove = (fileId: string) => {
    console.log("File removed:", fileId)
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-2xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <p className="text-muted-foreground">Drag and drop files or click to browse</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Upload Files</CardTitle>
            <CardDescription>Upload your documents, images, and other files</CardDescription>
          </CardHeader>
          <CardContent>
            <FileUpload
              onFilesSelected={handleFilesSelected}
              onFileRemove={handleFileRemove}
              maxFiles={5}
              maxFileSize={100}
              acceptedFileTypes={["image/*", "application/pdf", ".doc", ".docx", ".txt"]}
            />
          </CardContent>
        </Card>

        
      </div>
    </div>
  )
}
