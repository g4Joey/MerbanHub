// search-page-content.tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, X } from "lucide-react";
import { SearchFilters } from "./search-filters";
import { SearchResults } from "./search-results";
import { searchDocuments } from "@/lib/search";
import type {
  SearchFilters as SearchFiltersType,
  SearchResponse,
} from "@/lib/search"; // Import SearchResponse

export function SearchPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Initialize filters from URL params
  const [filters, setFilters] = useState<SearchFiltersType>(() => {
    return {
      clientName: searchParams.get("clientName") || "",
      accountNumber: searchParams.get("accountNumber") || "",
      // Add other filter initializations if they exist in SearchFiltersType
      // e.g., fileExtensions: searchParams.get("fileExtensions")?.split(',') || [],
      // Ensure all possible filters are initialized here, even if empty/default
    };
  });

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      // Ensure only non-empty or non-zero values are added to URL
      if (value) {
        // Catches null, undefined, empty string, 0 (for numbers)
        if (Array.isArray(value)) {
          if (value.length > 0) {
            params.set(key, value.join(","));
          }
        } else if (
          value !== "" &&
          value !== 0 &&
          value !== undefined &&
          value !== null
        ) {
          params.set(key, value.toString());
        }
      }
    });

    const queryString = params.toString();
    const newUrl = queryString
      ? `/dashboard/search?${queryString}`
      : "/dashboard/search";
    // Use shallow routing to prevent full page reloads for filter changes
    router.replace(newUrl, { scroll: false, shallow: true });
  }, [filters, router]);

  // Determine if any active filters exist to enable the query and show clear button
  // This logic correctly determines if any filter value is non-empty/non-zero/non-empty array
  const hasActiveFilters = Object.values(filters).some((value) =>
    Array.isArray(value)
      ? value.length > 0
      : value !== "" && value !== 0 && value !== undefined && value !== null
  );

  // Fetch search results using react-query
  const {
    data: results, // `results` will be of type `SearchResponse` or `undefined`
    isLoading,
    error,
  } = useQuery<SearchResponse, Error>({
    // Explicitly type the useQuery hook for better type safety
    queryKey: ["search", filters], // Query key changes when filters change, triggering refetch
    queryFn: () => searchDocuments(filters), // Calls your updated searchDocuments function
    enabled: hasActiveFilters, // Only run the query if there are active filters
  });

  // --- DEBUGGING CONSOLE LOGS ---
  console.log("--- SearchPageContent State ---");
  console.log("Current Filters:", filters);
  console.log("Has Active Filters:", hasActiveFilters);
  console.log("Is Loading:", isLoading);
  console.log("Error:", error);
  console.log("API Results Data:", results);
  console.log("-------------------------------");
  // --- END DEBUGGING CONSOLE LOGS ---

  const handleFilterChange = (newFilters: Partial<SearchFiltersType>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const clearAllFilters = () => {
    setFilters({
      clientName: "",
      accountNumber: "",
      // Ensure all filter properties are reset to their default values here
      // e.g., fileExtensions: [],
      // e.g., fileSizeMin: 0,
      // e.g., fileSizeMax: 100000,
    });
  };

  const removeFilter = (filterKey: keyof SearchFiltersType) => {
    // This logic needs to correctly reset the specific filter type
    if (filterKey === "fileExtensions") {
      setFilters((prev) => ({ ...prev, [filterKey]: [] as any })); // Use 'as any' for complex types if needed or ensure correct type casting
    } else if (
      filterKey === "fileSizeMin" ||
      filterKey === "ocrConfidenceMin"
    ) {
      setFilters((prev) => ({ ...prev, [filterKey]: 0 as any }));
    } else if (filterKey === "fileSizeMax") {
      setFilters((prev) => ({ ...prev, [filterKey]: 100000 as any })); // Assuming 100000 is your default max
    } else {
      setFilters((prev) => ({ ...prev, [filterKey]: "" as any }));
    }
  };

  const getActiveFilters = () => {
    const active: Array<{
      key: keyof SearchFiltersType;
      label: string;
      value: string;
    }> = [];

    if (filters.clientName)
      active.push({
        key: "clientName",
        label: "Client",
        value: filters.clientName,
      });
    if (filters.accountNumber)
      active.push({
        key: "accountNumber",
        label: "Account",
        value: filters.accountNumber,
      });
    // Add logic for other active filters if you expand your filter options

    return active;
  };

  const activeFilters = getActiveFilters();
  // `hasActiveFilters` is already computed above this function

  return (
    <div className="grid lg:grid-cols-[300px_1fr] gap-6">
      {/* Filters Sidebar */}
      <div className="space-y-6">
        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Filters</CardTitle>
              {hasActiveFilters && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearAllFilters}
                  className="text-xs bg-transparent"
                >
                  Clear All
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {/* Ensure `SearchFilters` correctly updates `filters` state via `onFilterChange` */}
            <SearchFilters
              filters={filters}
              onFilterChange={handleFilterChange}
            />
          </CardContent>
        </Card>
      </div>

      {/* Results Area */}
      <div className="space-y-6">
        {/* Active Filters */}
        {hasActiveFilters && ( // Only show this card if there are active filters
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-wrap gap-2">
                {activeFilters.map((filter) => (
                  <Badge
                    key={filter.key}
                    variant="secondary"
                    className="flex items-center gap-1 px-3 py-1"
                  >
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

        {/* Search Results Display Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Search Results
              {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
              {/* Only show total if results is available and documents array exists */}
              {results && results.documents ? (
                <Badge variant="outline" className="ml-auto">
                  {results.total} documents
                </Badge>
              ) : null}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!hasActiveFilters ? (
              // Path 1: No filters applied yet
              <div className="text-center py-12 text-muted-foreground">
                <p>Apply filters to search for documents</p>
              </div>
            ) : isLoading ? (
              // Path 2: Data is currently loading
              <div className="text-center py-12">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
                <p className="text-muted-foreground">Searching documents...</p>
              </div>
            ) : error ? (
              // Path 3: An error occurred during fetching
              <div className="text-center py-12 text-destructive">
                <p>Error loading search results. Please try again.</p>
                <p className="text-sm mt-2">{error.message}</p>{" "}
                {/* Display the actual error message */}
              </div>
            ) : results && results.documents.length === 0 ? (
              // Path 4: API returned successfully, but no documents match criteria
              <div className="text-center py-12 text-muted-foreground">
                <p>No documents found matching your criteria.</p>
                <p className="text-sm mt-2">Try adjusting your filters.</p>
              </div>
            ) : results && results.documents.length > 0 ? (
              // Path 5: API returned documents, display them
              <SearchResults results={results.documents} />
            ) : (
              // Fallback for any unexpected state (should ideally not be reached)
              <div className="text-center py-12 text-muted-foreground">
                <p>An unexpected state occurred. Please try refreshing.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
