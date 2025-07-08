"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Loader2, X } from "lucide-react"
import { SearchFilters } from "./search-filters"
import { SearchResults } from "./search-results"
import { searchDocuments } from "@/lib/search"
import type { SearchFilters as SearchFiltersType } from "@/lib/search"

export function SearchPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()

  // Initialize filters from URL params
  const [filters, setFilters] = useState<SearchFiltersType>(() => {
    return {
      clientName: searchParams.get("clientName") || "",
      accountNumber: searchParams.get("accountNumber") || "",
      department: searchParams.get("department") || "",
      fundDateStart: searchParams.get("fundDateStart") || "",
      fundDateEnd: searchParams.get("fundDateEnd") || "",
      fileExtensions: searchParams.get("fileExtensions")?.split(",").filter(Boolean) || [],
      dateModifiedStart: searchParams.get("dateModifiedStart") || "",
      dateModifiedEnd: searchParams.get("dateModifiedEnd") || "",
      fileSizeMin: Number.parseInt(searchParams.get("fileSizeMin") || "0"),
      fileSizeMax: Number.parseInt(searchParams.get("fileSizeMax") || "100000"),
      ocrConfidenceMin: Number.parseInt(searchParams.get("ocrConfidenceMin") || "0"),
      indexStatus: searchParams.get("indexStatus") || "",
      fullTextSearch: searchParams.get("fullTextSearch") || "",
    }
  })

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams()

    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        if (Array.isArray(value)) {
          if (value.length > 0) {
            params.set(key, value.join(","))
          }
        } else if (value !== "" && value !== 0) {
          params.set(key, value.toString())
        }
      }
    })

    const queryString = params.toString()
    const newUrl = queryString ? `/dashboard/search?${queryString}` : "/dashboard/search"
    router.replace(newUrl, { scroll: false })
  }, [filters, router])

  // Fetch search results
  const {
    data: results,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["search", filters],
    queryFn: () => searchDocuments(filters),
    enabled: Object.values(filters).some((value) =>
      Array.isArray(value) ? value.length > 0 : value !== "" && value !== 0,
    ),
  })

  const handleFilterChange = (newFilters: Partial<SearchFiltersType>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }))
  }

  const clearAllFilters = () => {
    setFilters({
      clientName: "",
      accountNumber: "",
      department: "",
      fundDateStart: "",
      fundDateEnd: "",
      fileExtensions: [],
      dateModifiedStart: "",
      dateModifiedEnd: "",
      fileSizeMin: 0,
      fileSizeMax: 100000,
      ocrConfidenceMin: 0,
      indexStatus: "",
      fullTextSearch: "",
    })
  }

  const removeFilter = (filterKey: keyof SearchFiltersType) => {
    if (filterKey === "fileExtensions") {
      setFilters((prev) => ({ ...prev, [filterKey]: [] }))
    } else if (filterKey === "fileSizeMin" || filterKey === "ocrConfidenceMin") {
      setFilters((prev) => ({ ...prev, [filterKey]: 0 }))
    } else if (filterKey === "fileSizeMax") {
      setFilters((prev) => ({ ...prev, [filterKey]: 100000 }))
    } else {
      setFilters((prev) => ({ ...prev, [filterKey]: "" }))
    }
  }

  const getActiveFilters = () => {
    const active: Array<{ key: keyof SearchFiltersType; label: string; value: string }> = []

    if (filters.clientName) active.push({ key: "clientName", label: "Client", value: filters.clientName })
    if (filters.accountNumber) active.push({ key: "accountNumber", label: "Account", value: filters.accountNumber })
    if (filters.department) active.push({ key: "department", label: "Department", value: filters.department })
    if (filters.fundDateStart || filters.fundDateEnd) {
      const dateRange = `${filters.fundDateStart || "Start"} - ${filters.fundDateEnd || "End"}`
      active.push({ key: "fundDateStart", label: "Fund Date", value: dateRange })
    }
    if (filters.fileExtensions.length > 0) {
      active.push({ key: "fileExtensions", label: "File Types", value: filters.fileExtensions.join(", ") })
    }
    if (filters.dateModifiedStart || filters.dateModifiedEnd) {
      const dateRange = `${filters.dateModifiedStart || "Start"} - ${filters.dateModifiedEnd || "End"}`
      active.push({ key: "dateModifiedStart", label: "Modified Date", value: dateRange })
    }
    if (filters.fileSizeMin > 0 || filters.fileSizeMax < 100000) {
      active.push({
        key: "fileSizeMin",
        label: "File Size",
        value: `${filters.fileSizeMin} - ${filters.fileSizeMax} KB`,
      })
    }
    if (filters.ocrConfidenceMin > 0) {
      active.push({ key: "ocrConfidenceMin", label: "OCR Confidence", value: `≥ ${filters.ocrConfidenceMin}%` })
    }
    if (filters.indexStatus) active.push({ key: "indexStatus", label: "Status", value: filters.indexStatus })
    if (filters.fullTextSearch)
      active.push({ key: "fullTextSearch", label: "Full Text", value: filters.fullTextSearch })

    return active
  }

  const activeFilters = getActiveFilters()
  const hasActiveFilters = activeFilters.length > 0

  return (
    <div className="grid lg:grid-cols-[300px_1fr] gap-6">
      {/* Filters Sidebar */}
      <div className="space-y-6">
        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Filters</CardTitle>
              {hasActiveFilters && (
                <Button variant="outline" size="sm" onClick={clearAllFilters} className="text-xs bg-transparent">
                  Clear All
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <SearchFilters filters={filters} onFilterChange={handleFilterChange} />
          </CardContent>
        </Card>
      </div>

      {/* Results Area */}
      <div className="space-y-6">
        {/* Active Filters */}
        {hasActiveFilters && (
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-wrap gap-2">
                {activeFilters.map((filter) => (
                  <Badge key={filter.key} variant="secondary" className="flex items-center gap-1 px-3 py-1">
                    <span className="font-medium">{filter.label}:</span>
                    <span>{filter.value}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-4 w-4 p-0 hover:bg-transparent"
                      onClick={() => removeFilter(filter.key)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Search Results */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Search Results
              {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
              {results && (
                <Badge variant="outline" className="ml-auto">
                  {results.total} documents
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!hasActiveFilters ? (
              <div className="text-center py-12 text-muted-foreground">
                <p>Apply filters to search for documents</p>
              </div>
            ) : isLoading ? (
              <div className="text-center py-12">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
                <p className="text-muted-foreground">Searching documents...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12 text-destructive">
                <p>Error loading search results. Please try again.</p>
              </div>
            ) : results && results.documents.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <p>No documents found matching your criteria.</p>
                <p className="text-sm mt-2">Try adjusting your filters.</p>
              </div>
            ) : (
              <SearchResults results={results?.documents || []} />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
