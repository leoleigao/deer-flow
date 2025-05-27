// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useState } from "react";
import { TableGuideApp } from "~/components/table-guide/TableGuideApp";

export default function TableGuidePage() {
  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Table Guide Generator</h1>
        <p className="text-muted-foreground mb-8">
          Generate comprehensive documentation and analysis for your database tables using AI-powered research agents.
        </p>
        <TableGuideApp />
      </div>
    </div>
  );
} 