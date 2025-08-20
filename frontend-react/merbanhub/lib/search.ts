// search.ts
import type { SearchFilters, SearchResponse } from "@/lib/search";

export async function searchDocuments(
  filters: SearchFilters
): Promise<SearchResponse> {
  console.log("Sending filters to backend for search:", filters);

  try {
    const url = "http://localhost:8080/api/documents/search";

    // ✅ Retrieve token from localStorage
    const token = localStorage.getItem("jwtToken");
    if (!token) {
      throw new Error("No authentication token found. Please log in.");
    }

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        Authorization: `Bearer ${token}`, // ✅ use token from localStorage
      },
      body: JSON.stringify(filters),
    });

    if (!response.ok) {
      let errorDetail = `HTTP error! Status: ${response.status}`;
      try {
        const errorBody = await response.json();
        errorDetail = errorBody?.message || JSON.stringify(errorBody);
      } catch {
        errorDetail = response.statusText;
      }
      console.log("API call failed:", errorDetail);
      throw new Error(`Failed to fetch documents: ${errorDetail}`);
    }

    const data: SearchResponse = await response.json();
    console.log("Received data from backend:", data);

    if (!data || !Array.isArray(data.documents)) {
      console.error(
        "API response missing 'documents' array or is malformed:",
        data
      );
      throw new Error("Invalid response format: 'documents' array is missing.");
    }

    return data;
  } catch (error: any) {
    console.error(
      "Error during document search API call:",
      error.message || error
    );
    throw error;
  }
}

// OCR-specific search function
export async function searchOcrFiles(query: string): Promise<any> {
  console.log("Searching OCR files with query:", query);

  try {
    const url = `http://localhost:8080/api/ocr/search?q=${encodeURIComponent(query)}`;

    const token = localStorage.getItem("jwtToken");
    if (!token) {
      throw new Error("No authentication token found. Please log in.");
    }

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      let errorDetail = `HTTP error! Status: ${response.status}`;
      try {
        const errorBody = await response.json();
        errorDetail = errorBody?.message || JSON.stringify(errorBody);
      } catch {
        errorDetail = response.statusText;
      }
      console.log("OCR search API call failed:", errorDetail);
      throw new Error(`Failed to search OCR files: ${errorDetail}`);
    }

    const data = await response.json();
    console.log("Received OCR search data:", data);

    return data;
  } catch (error: any) {
    console.error("Error during OCR search API call:", error.message || error);
    throw error;
  }
}

// Get OCR processing stats
export async function getOcrStats(): Promise<any> {
  try {
    const url = "http://localhost:8080/api/ocr/stats";

    const token = localStorage.getItem("jwtToken");
    if (!token) {
      throw new Error("No authentication token found. Please log in.");
    }

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch OCR stats: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("OCR stats:", data);

    return data;
  } catch (error: any) {
    console.error("Error getting OCR stats:", error.message || error);
    throw error;
  }
}

// Trigger OCR processing
export async function triggerOcrProcessing(): Promise<any> {
  try {
    const url = "http://localhost:8080/api/ocr/trigger";

    const token = localStorage.getItem("jwtToken");
    if (!token) {
      throw new Error("No authentication token found. Please log in.");
    }

    const response = await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to trigger OCR: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("OCR trigger response:", data);

    return data;
  } catch (error: any) {
    console.error("Error triggering OCR:", error.message || error);
    throw error;
  }
}
