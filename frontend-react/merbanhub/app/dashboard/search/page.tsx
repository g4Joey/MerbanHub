"use client"

import { Suspense } from "react"
import { SearchPageContent } from "@/components/search-page-content"

export default function SearchPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Document Search</h1>
        <p className="text-muted-foreground mt-2">Search and filter documents using advanced criteria</p>
      </div>

      <Suspense fallback={<div>Loading search interface...</div>}>
        <SearchPageContent />
      </Suspense>
    </div>
  )
}
