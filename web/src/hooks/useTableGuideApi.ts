// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useState } from "react";
import { env } from "~/env";

interface TableGuideResponse {
  table: string;
  guide: string;
}

interface TableGuideError {
  detail: string;
}

interface FixtureTable {
  name: string;
  title: string;
  description: string;
  doc_count: number;
}

interface FixturesIndexResponse {
  tables: FixtureTable[];
}

export function useTableGuideApi() {
  const [isLoading, setIsLoading] = useState(false);

  const getFixturesIndex = async (): Promise<FixtureTable[]> => {
    try {
      const apiUrl = env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const url = `${apiUrl}/api/fixtures_index`;
      
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: FixturesIndexResponse = await response.json();
      return data.tables;
    } catch (error) {
      console.warn("Failed to fetch fixtures index:", error);
      // Return fallback list if API fails
      return [
        { name: "tracking.AdClickEvent", title: "Ad Click Event", description: "User ad click tracking", doc_count: 0 },
        { name: "marketing.CampaignSummary", title: "Campaign Summary", description: "Marketing campaign data", doc_count: 0 },
        { name: "sales.OrderHeader", title: "Order Header", description: "Sales order information", doc_count: 0 },
        { name: "user.ProfileSnapshot", title: "User Profile", description: "User profile data", doc_count: 0 },
        { name: "finance.InvoiceItem", title: "Invoice Item", description: "Financial invoice details", doc_count: 0 },
        { name: "event.FunnelStep", title: "Funnel Step", description: "User funnel analytics", doc_count: 0 },
        { name: "tracking.PageView", title: "Page View", description: "Page view tracking", doc_count: 0 }
      ];
    }
  };

  const generateGuide = async (tableName: string): Promise<TableGuideResponse> => {
    setIsLoading(true);
    
    try {
      // Get API URL from environment or default to localhost
      const apiUrl = env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const url = `${apiUrl}/api/table_guide?table=${encodeURIComponent(tableName)}`;
      
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
          const errorData: TableGuideError = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // If we can't parse the error response, use the default message
        }
        
        throw new Error(errorMessage);
      }

      const data: TableGuideResponse = await response.json();
      
      // Validate the response structure
      if (!data.guide || typeof data.guide !== "string") {
        throw new Error("Invalid response: missing or invalid guide content");
      }
      
      return data;
    } catch (error) {
      // Re-throw with more context if it's a network error
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new Error(
          "Failed to connect to the API server. Please ensure the backend is running."
        );
      }
      
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    generateGuide,
    getFixturesIndex,
    isLoading,
  };
} 