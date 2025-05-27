// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useState, useEffect } from "react";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select";
import { Alert, AlertDescription } from "~/components/ui/alert";
import { Loader2, AlertCircle, CheckCircle2 } from "lucide-react";
import { MarkdownRenderer } from "~/components/table-guide/MarkdownRenderer";
import { useTableGuideApi } from "~/hooks/useTableGuideApi";

type AppState = "idle" | "loading" | "success" | "error";

interface FixtureTable {
  name: string;
  title: string;
  description: string;
  doc_count: number;
}

export function TableGuideApp() {
  const [state, setState] = useState<AppState>("idle");
  const [tableName, setTableName] = useState("");
  const [markdownContent, setMarkdownContent] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [availableTables, setAvailableTables] = useState<FixtureTable[]>([]);
  
  const { generateGuide, getFixturesIndex, isLoading } = useTableGuideApi();

  // Telemetry helper
  const emitTelemetry = (event: string, data?: Record<string, any>) => {
    if (process.env.NODE_ENV === "test") return; // Skip telemetry in tests
    
    // Only emit telemetry if analytics is available and GDPR compliance is met
    if (typeof window !== "undefined" && (window as any).amplitude && process.env.NEXT_PUBLIC_AMPLITUDE_API_KEY) {
      (window as any).amplitude.track(event, {
        ...data,
        table: tableName,
        timestamp: new Date().toISOString(),
      });
    }
  };

  // Load available tables on component mount
  useEffect(() => {
    const loadTables = async () => {
      try {
        const tables = await getFixturesIndex();
        setAvailableTables(tables);
      } catch (error) {
        console.warn("Failed to load available tables:", error);
      }
    };
    
    loadTables();
  }, [getFixturesIndex]);

  const handleGenerate = async () => {
    if (!tableName.trim()) {
      setErrorMessage("Please enter a table name");
      setState("error");
      return;
    }

    setState("loading");
    setErrorMessage("");
    
    // Emit telemetry for guide request
    emitTelemetry("ui.table_guide.requested", {
      table_name: tableName.trim(),
      source: "manual_input"
    });
    
    try {
      const result = await generateGuide(tableName.trim());
      setMarkdownContent(result.guide);
      setState("success");
      
      // Emit telemetry for successful generation
      emitTelemetry("ui.table_guide.rendered", {
        table_name: tableName.trim(),
        guide_length: result.guide.length,
        success: true
      });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to generate guide");
      setState("error");
      
      // Emit telemetry for failed generation
      emitTelemetry("ui.table_guide.error", {
        table_name: tableName.trim(),
        error_message: error instanceof Error ? error.message : "Unknown error"
      });
    }
  };

  const handleReset = () => {
    setState("idle");
    setMarkdownContent("");
    setErrorMessage("");
  };

  const handleExampleSelect = (value: string) => {
    setTableName(value);
    if (state === "error") {
      setState("idle");
      setErrorMessage("");
    }
    
    // Emit telemetry for example selection
    emitTelemetry("ui.table_guide.example_selected", {
      table_name: value,
      source: "dropdown"
    });
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle>Generate Table Guide</CardTitle>
          <CardDescription>
            Enter a table name to generate comprehensive documentation and analysis.
            {process.env.NODE_ENV === "development" && (
              <span className="block mt-1 text-amber-600">
                Running in stub mode - using local fixture data.
              </span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="table-name">Table Name</Label>
            <Input
              id="table-name"
              placeholder="e.g., tracking.AdClickEvent"
              value={tableName}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTableName(e.target.value)}
              disabled={isLoading}
              onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => {
                if (e.key === "Enter" && !isLoading) {
                  handleGenerate();
                }
              }}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="example-select">Or choose an example:</Label>
            <Select onValueChange={handleExampleSelect} disabled={isLoading}>
              <SelectTrigger id="example-select" data-testid="example-select">
                <SelectValue placeholder="Select an example table..." />
              </SelectTrigger>
              <SelectContent>
                {availableTables.map((table) => (
                  <SelectItem key={table.name} value={table.name}>
                    <div className="flex flex-col">
                      <span className="font-medium">{table.name}</span>
                      {table.description && (
                        <span className="text-xs text-muted-foreground">{table.description}</span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex gap-2">
            <Button 
              onClick={handleGenerate} 
              disabled={isLoading || !tableName.trim()}
              className="flex-1"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" data-testid="loading-spinner" />
                  Generating...
                </>
              ) : (
                "Generate Guide"
              )}
            </Button>
            
            {state !== "idle" && (
              <Button variant="outline" onClick={handleReset} disabled={isLoading}>
                Reset
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Status Messages */}
      {state === "error" && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}

      {state === "success" && (
        <Alert>
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>
            Table guide generated successfully! Scroll down to view the results.
          </AlertDescription>
        </Alert>
      )}

      {/* Results Section */}
      {state === "success" && markdownContent && (
        <Card>
          <CardHeader>
            <CardTitle>Generated Guide: {tableName}</CardTitle>
            <CardDescription>
              AI-generated documentation and analysis for your table.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <MarkdownRenderer content={markdownContent} />
          </CardContent>
        </Card>
      )}
    </div>
  );
} 