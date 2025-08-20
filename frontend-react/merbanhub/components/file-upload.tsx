
"use client";

import type React from "react";
import { useCallback, useState } from "react";
import { Upload, X, File, ImageIcon, Video, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface FileWithProgress {
  file: File;
  progress: number;
  id: string;
  status: "uploading" | "completed" | "error";
}

interface FileUploadProps {
  onFilesSelected?: (files: File[]) => void;
  onFileRemove?: (fileId: string) => void;
  maxFiles?: number;
  maxFileSize?: number; // in MB
  acceptedFileTypes?: string[];
  className?: string;
}

const getFileIcon = (fileType: string) => {
  if (fileType.startsWith("image/")) return ImageIcon;
  if (fileType.startsWith("video/")) return Video;
  if (fileType.includes("pdf") || fileType.includes("document"))
    return FileText;
  return File;
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return (
    Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  );
};

export function FileUpload({
  onFilesSelected,
  onFileRemove,
  maxFiles = 10,
  maxFileSize = 10,
  acceptedFileTypes = ["image/*", "application/pdf", ".doc", ".docx"],
  className,
}: FileUploadProps) {
  const [files, setFiles] = useState<FileWithProgress[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);

  
  // This function will now handle the actual upload to your backend and trigger OCR
  const uploadFileToServer = useCallback(
    async (fileToUpload: FileWithProgress) => {
      const formData = new FormData();
      formData.append("file", fileToUpload.file);

      // get token from localStorage
      const token = localStorage.getItem("jwtToken");

      try {
        // Upload to OCR endpoint instead of regular file upload
        const response = await fetch("http://localhost:8080/api/ocr/upload", {
          method: "POST",
          headers: {
            Authorization: token ? `Bearer ${token}` : "", // attach JWT if available
          },
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          console.log("OCR upload successful:", result);
          
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileToUpload.id
                ? { ...f, progress: 100, status: "completed" }
                : f
            )
          );
          
          // Optionally trigger a notification or callback
          if (result.processing) {
            console.log("OCR processing started for:", fileToUpload.file.name);
          }
        } else {
          console.error("Upload failed:", response.statusText);
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileToUpload.id ? { ...f, status: "error" } : f
            )
          );
        }
      } catch (error) {
        console.error("Error during upload:", error);
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileToUpload.id ? { ...f, status: "error" } : f
          )
        );
      }
    },
    []
  );

  const handleFiles = useCallback(
    (newFiles: File[]) => {
      const validFiles = newFiles.filter((file) => {
        const isValidSize = file.size <= maxFileSize * 1024 * 1024;
        const isValidType = acceptedFileTypes.some(
          (type) =>
            type === "*" ||
            file.type.match(type.replace("*", ".*")) ||
            file.name.toLowerCase().endsWith(type.toLowerCase())
        );
        return isValidSize && isValidType;
      });

      if (files.length + validFiles.length > maxFiles) {
        alert(`Maximum ${maxFiles} files allowed`);
        return;
      }

      const filesWithProgress: FileWithProgress[] = validFiles.map((file) => ({
        file,
        progress: 0,
        id: Math.random().toString(36).substr(2, 9),
        status: "uploading",
      }));

      setFiles((prev) => [...prev, ...filesWithProgress]);
      onFilesSelected?.(validFiles);

      // Instead of simulating, actually upload
      filesWithProgress.forEach((f) => uploadFileToServer(f));
    },
    [
      files.length,
      maxFiles,
      maxFileSize,
      acceptedFileTypes,
      onFilesSelected,
      uploadFileToServer,
    ]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);

      const droppedFiles = Array.from(e.dataTransfer.files);
      handleFiles(droppedFiles);
    },
    [handleFiles]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        const selectedFiles = Array.from(e.target.files);
        handleFiles(selectedFiles);
      }
    },
    [handleFiles]
  );

  const removeFile = useCallback(
    (fileId: string) => {
      setFiles((prev) => prev.filter((f) => f.id !== fileId));
      onFileRemove?.(fileId);
    },
    [onFileRemove]
  );

  return (
    <div className={cn("w-full space-y-4", className)}>
      {/* Drop Zone */}
      <Card
        className={cn(
          "border-2 border-dashed transition-colors duration-200",
          isDragOver
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-muted-foreground/50"
        )}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <CardContent className="flex flex-col items-center justify-center py-12 px-6 text-center">
          <Upload
            className={cn(
              "h-12 w-12 mb-4 transition-colors",
              isDragOver ? "text-primary" : "text-muted-foreground"
            )}
          />
          <div className="space-y-2">
            <p className="text-lg font-medium text-foreground">
              {isDragOver ? "Drop files here" : "Drag & drop files here"}
            </p>
            <p className="text-sm text-muted-foreground">
              or click to browse files
            </p>
            <p className="text-xs text-muted-foreground">
              Max {maxFiles} files, {maxFileSize}MB each
            </p>
          </div>
          <Button
            variant="default"
            className="mt-4"
            onClick={() => document.getElementById("file-input")?.click()}
          >
            Choose Files
          </Button>
          <input
            id="file-input"
            type="file"
            multiple
            className="hidden"
            accept={acceptedFileTypes.join(",")}
            onChange={handleFileInput}
          />
        </CardContent>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-foreground">
            Uploaded Files ({files.length})
          </h3>
          <div className="space-y-2">
            {files.map((fileItem) => {
              const FileIcon = getFileIcon(fileItem.file.type);
              return (
                <Card key={fileItem.id} className="p-3">
                  <div className="flex items-center space-x-3">
                    <FileIcon className="h-8 w-8 text-muted-foreground flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm font-medium text-foreground truncate">
                          {fileItem.file.name}
                        </p>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive"
                          onClick={() => removeFile(fileItem.id)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
                        <span>{formatFileSize(fileItem.file.size)}</span>
                        <span
                          className={cn(
                            "font-medium",
                            fileItem.status === "completed" && "text-primary",
                            fileItem.status === "error" && "text-destructive"
                          )}
                        >
                          {fileItem.status === "uploading" &&
                            `${Math.round(fileItem.progress)}%`}
                          {fileItem.status === "completed" && "Complete"}
                          {fileItem.status === "error" && "Error"}
                        </span>
                      </div>
                      {fileItem.status === "uploading" && (
                        <Progress value={fileItem.progress} className="h-1.5" />
                      )}
                      {fileItem.status === "completed" && (
                        <div className="h-1.5 bg-primary/20 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full w-full transition-all duration-300"
                            style={{ width: "100%" }}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}