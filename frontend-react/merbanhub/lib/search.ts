import type { SearchFilters, SearchResponse } from "@/lib/search"

// Mock data for UI demonstration - replace with actual API calls to Spring Boot backend
const mockDocuments = [
  {
    id: "1",
    fileName: "Investment_Agreement_2024_Q1.pdf",
    clientName: "Acme Corporation",
    accountNumber: "ACC-001-2024",
    department: "Investment",
    fundDate: "2024-01-15",
    fileExtension: "pdf",
    dateModified: "2024-01-20",
    fileSize: 2048000,
    ocrConfidence: 95,
    indexStatus: "Indexed",
    snippet: "This investment agreement outlines the terms and conditions for the Q1 2024 funding round...",
    filePath: "/documents/investment/2024/q1/investment_agreement.pdf",
  },
  {
    id: "2",
    fileName: "Compliance_Report_December.docx",
    clientName: "Beta Industries",
    accountNumber: "ACC-002-2023",
    department: "Compliance",
    fundDate: "2023-12-01",
    fileExtension: "docx",
    dateModified: "2023-12-15",
    fileSize: 1024000,
    ocrConfidence: 88,
    indexStatus: "Indexed",
    snippet: "Monthly compliance report covering regulatory requirements and audit findings...",
    filePath: "/documents/compliance/2023/december/compliance_report.docx",
  },
  {
    id: "3",
    fileName: "Risk_Assessment_Q4_2023.xlsx",
    clientName: "Gamma Holdings",
    accountNumber: "ACC-003-2023",
    department: "Risk Management",
    fundDate: "2023-10-01",
    fileExtension: "xlsx",
    dateModified: "2023-12-30",
    fileSize: 512000,
    ocrConfidence: 92,
    indexStatus: "Pending",
    snippet: "Quarterly risk assessment including market analysis and portfolio evaluation...",
    filePath: "/documents/risk/2023/q4/risk_assessment.xlsx",
  },
  {
    id: "4",
    fileName: "Legal_Opinion_Contract_Review.pdf",
    clientName: "Delta Enterprises",
    accountNumber: "ACC-004-2024",
    department: "Legal",
    fundDate: "2024-02-01",
    fileExtension: "pdf",
    dateModified: "2024-02-05",
    fileSize: 3072000,
    ocrConfidence: 97,
    indexStatus: "Indexed",
    snippet: "Legal opinion regarding contract terms and regulatory compliance requirements...",
    filePath: "/documents/legal/2024/february/legal_opinion.pdf",
  },
  {
    id: "5",
    fileName: "Client_Onboarding_Checklist.docx",
    clientName: "Epsilon Corp",
    accountNumber: "ACC-005-2024",
    department: "Client Services",
    fundDate: "2024-01-10",
    fileExtension: "docx",
    dateModified: "2024-01-12",
    fileSize: 256000,
    ocrConfidence: 85,
    indexStatus: "Error",
    snippet: "Comprehensive checklist for new client onboarding process and documentation requirements...",
    filePath: "/documents/client-services/2024/january/onboarding_checklist.docx",
  },
]

// TODO: Replace with actual Spring Boot API calls
export async function searchDocuments(filters: SearchFilters): Promise<SearchResponse> {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 800))

  // In production, this would be:
  // const response = await fetch('/api/documents/search', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(filters)
  // })
  // return response.json()

  let filteredDocuments = [...mockDocuments]

  // Apply filters (this logic will be handled by Spring Boot backend)
  if (filters.clientName) {
    filteredDocuments = filteredDocuments.filter((doc) =>
      doc.clientName.toLowerCase().includes(filters.clientName.toLowerCase()),
    )
  }

  if (filters.accountNumber) {
    filteredDocuments = filteredDocuments.filter((doc) => doc.accountNumber === filters.accountNumber)
  }

  if (filters.department) {
    filteredDocuments = filteredDocuments.filter((doc) => doc.department === filters.department)
  }

  if (filters.fundDateStart) {
    filteredDocuments = filteredDocuments.filter((doc) => new Date(doc.fundDate) >= new Date(filters.fundDateStart))
  }

  if (filters.fundDateEnd) {
    filteredDocuments = filteredDocuments.filter((doc) => new Date(doc.fundDate) <= new Date(filters.fundDateEnd))
  }

  if (filters.fileExtensions.length > 0) {
    filteredDocuments = filteredDocuments.filter((doc) => filters.fileExtensions.includes(doc.fileExtension))
  }

  if (filters.dateModifiedStart) {
    filteredDocuments = filteredDocuments.filter(
      (doc) => new Date(doc.dateModified) >= new Date(filters.dateModifiedStart),
    )
  }

  if (filters.dateModifiedEnd) {
    filteredDocuments = filteredDocuments.filter(
      (doc) => new Date(doc.dateModified) <= new Date(filters.dateModifiedEnd),
    )
  }

  if (filters.fileSizeMin > 0) {
    filteredDocuments = filteredDocuments.filter((doc) => doc.fileSize >= filters.fileSizeMin * 1024)
  }

  if (filters.fileSizeMax < 100000) {
    filteredDocuments = filteredDocuments.filter((doc) => doc.fileSize <= filters.fileSizeMax * 1024)
  }

  if (filters.ocrConfidenceMin > 0) {
    filteredDocuments = filteredDocuments.filter((doc) => doc.ocrConfidence >= filters.ocrConfidenceMin)
  }

  if (filters.indexStatus) {
    filteredDocuments = filteredDocuments.filter((doc) => doc.indexStatus === filters.indexStatus)
  }

  if (filters.fullTextSearch) {
    filteredDocuments = filteredDocuments.filter(
      (doc) =>
        doc.fileName.toLowerCase().includes(filters.fullTextSearch.toLowerCase()) ||
        doc.snippet?.toLowerCase().includes(filters.fullTextSearch.toLowerCase()),
    )
  }

  return {
    documents: filteredDocuments,
    total: filteredDocuments.length,
    page: 1,
    pageSize: 20,
    totalPages: Math.ceil(filteredDocuments.length / 20),
  }
}

// TODO: Replace with actual Spring Boot API calls
export async function getDepartments(): Promise<string[]> {
  // In production: const response = await fetch('/api/filters/departments')
  return ["Accounting", "Legal", "Operations", "Compliance", "Risk Management", "Investment", "Client Services"]
}

// TODO: Replace with actual Spring Boot API calls
export async function searchClients(query: string): Promise<string[]> {
  // In production: const response = await fetch(`/api/filters/clients?q=${query}`)
  const mockClients = ["Acme Corporation", "Beta Industries", "Gamma Holdings", "Delta Enterprises", "Epsilon Corp"]
  return mockClients.filter((client) => client.toLowerCase().includes(query.toLowerCase()))
}
