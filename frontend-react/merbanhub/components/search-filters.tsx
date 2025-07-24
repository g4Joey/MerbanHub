"use client"
//search-filters.tsx  
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Slider } from "@/components/ui/slider"
import { Separator } from "@/components/ui/separator"
import type { SearchFilters as SearchFiltersType } from "@/lib/search"

interface SearchFiltersProps {
  filters: SearchFiltersType
  onFilterChange: (filters: Partial<SearchFiltersType>) => void
}
// But the features 
// Like the preview and download stay
// Fund range
// Date modified 
// The departments are Accounts&Compliance

// File extensions are okay
// IHL-account opening
// fund management 
// stockbrokers 
// SDSL
// client service
// Pensions
// Marketing 
// Govt securities

const departments = [
  "Accounts&Compliance",
  "IHL Account Opening",
  "Fund Management",
  "Stockbrokers",
  "SDSL",
  "client service",
  "Pensions",
  "Marketing",
  "Govt Securities",
]

const fileExtensions = [
  { value: "pdf", label: "PDF" },
  { value: "docx", label: "Word Document" },
  { value: "xlsx", label: "Excel" },
  { value: "pptx", label: "PowerPoint" },
  { value: "txt", label: "Text File" },
  { value: "jpg", label: "JPEG Image" },
  { value: "png", label: "PNG Image" },
]

const indexStatuses = ["Indexed", "Pending", "Error", "Processing"]

export function SearchFilters({ filters, onFilterChange }: SearchFiltersProps) {
  const handleFileExtensionChange = (extension: string, checked: boolean) => {
    const newExtensions = checked
      ? [...filters.fileExtensions, extension]
      : filters.fileExtensions.filter((ext) => ext !== extension)

    onFilterChange({ fileExtensions: newExtensions })
  }

  return (
    <div className="space-y-6">
      {/* Full Text Search */}
      {/* <div className="space-y-2">
        <Label htmlFor="fullTextSearch">Full Text Search</Label>
        <Input
          id="fullTextSearch"
          placeholder="Search document content..."
          value={filters.fullTextSearch}
          onChange={(e) => onFilterChange({ fullTextSearch: e.target.value })}
        />
      </div> */}

      <Separator />

      {/* Client Name */}
      <div className="space-y-2">
        <Label htmlFor="clientName">Client Name</Label>
        <Input
          id="clientName"
          placeholder="Enter client name..."
          value={filters.clientName}
          onChange={(e) => onFilterChange({ clientName: e.target.value })}
        />
      </div>

      {/* Account Number */}
      <div className="space-y-2">
        <Label htmlFor="accountNumber">Account Number</Label>
        <Input
          id="accountNumber"
          placeholder="Enter account number..."
          value={filters.accountNumber}
          onChange={(e) => onFilterChange({ accountNumber: e.target.value })}
        />
      </div>

      
    </div>
  );
}
