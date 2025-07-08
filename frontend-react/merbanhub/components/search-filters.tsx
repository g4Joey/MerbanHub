"use client"

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
      <div className="space-y-2">
        <Label htmlFor="fullTextSearch">Full Text Search</Label>
        <Input
          id="fullTextSearch"
          placeholder="Search document content..."
          value={filters.fullTextSearch}
          onChange={(e) => onFilterChange({ fullTextSearch: e.target.value })}
        />
      </div>

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

      {/* Department */}
      <div className="space-y-2">
        <Label>Department</Label>
        <Select value={filters.department} onValueChange={(value) => onFilterChange({ department: value })}>
          <SelectTrigger>
            <SelectValue placeholder="Select department..." />
          </SelectTrigger>
          <SelectContent>
            {departments.map((dept) => (
              <SelectItem key={dept} value={dept}>
                {dept}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Separator />

      {/* Fund Date Range */}
      <div className="space-y-2">
        <Label>Fund Date Range</Label>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <Label htmlFor="fundDateStart" className="text-xs text-muted-foreground">
              Start Date
            </Label>
            <Input
              id="fundDateStart"
              type="date"
              value={filters.fundDateStart}
              onChange={(e) => onFilterChange({ fundDateStart: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="fundDateEnd" className="text-xs text-muted-foreground">
              End Date
            </Label>
            <Input
              id="fundDateEnd"
              type="date"
              value={filters.fundDateEnd}
              onChange={(e) => onFilterChange({ fundDateEnd: e.target.value })}
            />
          </div>
        </div>
      </div>

      {/* Date Modified Range */}
      <div className="space-y-2">
        <Label>Date Modified Range</Label>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <Label htmlFor="dateModifiedStart" className="text-xs text-muted-foreground">
              Start Date
            </Label>
            <Input
              id="dateModifiedStart"
              type="date"
              value={filters.dateModifiedStart}
              onChange={(e) => onFilterChange({ dateModifiedStart: e.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="dateModifiedEnd" className="text-xs text-muted-foreground">
              End Date
            </Label>
            <Input
              id="dateModifiedEnd"
              type="date"
              value={filters.dateModifiedEnd}
              onChange={(e) => onFilterChange({ dateModifiedEnd: e.target.value })}
            />
          </div>
        </div>
      </div>

      <Separator />

      {/* File Extensions */}
      <div className="space-y-2">
        <Label>File Extensions</Label>
        <div className="grid grid-cols-2 gap-2">
          {fileExtensions.map((ext) => (
            <div key={ext.value} className="flex items-center space-x-2">
              <Checkbox
                id={ext.value}
                checked={filters.fileExtensions.includes(ext.value)}
                onCheckedChange={(checked) => handleFileExtensionChange(ext.value, checked as boolean)}
              />
              <Label htmlFor={ext.value} className="text-sm font-normal">
                {ext.label}
              </Label>
            </div>
          ))}
        </div>
      </div>

      {/* File Size Range */}
      <div className="space-y-2">
        <Label>File Size (KB)</Label>
        <div className="px-2">
          <Slider
            value={[filters.fileSizeMin, filters.fileSizeMax]}
            onValueChange={([min, max]) => onFilterChange({ fileSizeMin: min, fileSizeMax: max })}
            max={100000}
            min={0}
            step={100}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>{filters.fileSizeMin} KB</span>
            <span>{filters.fileSizeMax} KB</span>
          </div>
        </div>
      </div>

    </div>
  );
}
