"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  RefreshCw, 
  FileSearch, 
  Upload, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Play
} from "lucide-react";
import { getOcrStats, triggerOcrProcessing, searchOcrFiles } from "@/lib/search";

interface OcrStats {
  incoming: number;
  fully_indexed: number;
  partially_indexed: number;
  failed: number;
  error?: string;
}

interface OcrStatusProps {
  onTriggerUpload?: () => void;
  searchQuery?: string;
}

export function OcrStatus({ onTriggerUpload, searchQuery }: OcrStatusProps) {
  const [stats, setStats] = useState<OcrStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await getOcrStats();
      setStats(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error("Failed to fetch OCR stats:", error);
      setStats({ incoming: 0, fully_indexed: 0, partially_indexed: 0, failed: 0, error: "Failed to connect" });
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerOcr = async () => {
    setTriggering(true);
    try {
      await triggerOcrProcessing();
      // Refresh stats after triggering
      setTimeout(fetchStats, 2000);
    } catch (error) {
      console.error("Failed to trigger OCR:", error);
    } finally {
      setTriggering(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const getTotalProcessed = () => {
    if (!stats) return 0;
    return stats.fully_indexed + stats.partially_indexed;
  };

  const getTotalFiles = () => {
    if (!stats) return 0;
    return stats.incoming + stats.fully_indexed + stats.partially_indexed + stats.failed;
  };

  const getProcessingProgress = () => {
    const total = getTotalFiles();
    if (total === 0) return 100;
    return ((getTotalProcessed() + stats?.failed || 0) / total) * 100;
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <FileSearch className="h-5 w-5" />
            OCR Processing Status
          </CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchStats}
              disabled={loading}
              className="flex items-center gap-1"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            {onTriggerUpload && (
              <Button
                variant="default"
                size="sm"
                onClick={onTriggerUpload}
                className="flex items-center gap-1"
              >
                <Upload className="h-4 w-4" />
                Upload Files
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {stats?.error ? (
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">{stats.error}</span>
          </div>
        ) : (
          <>
            {/* Processing Progress */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Processing Progress</span>
                <span>{Math.round(getProcessingProgress())}%</span>
              </div>
              <Progress value={getProcessingProgress()} className="h-2" />
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-orange-50 dark:bg-orange-950 rounded-lg">
                <Clock className="h-6 w-6 mx-auto mb-2 text-orange-600" />
                <div className="text-2xl font-bold text-orange-600">{stats?.incoming || 0}</div>
                <div className="text-xs text-muted-foreground">Pending</div>
              </div>
              
              <div className="text-center p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                <CheckCircle className="h-6 w-6 mx-auto mb-2 text-green-600" />
                <div className="text-2xl font-bold text-green-600">{stats?.fully_indexed || 0}</div>
                <div className="text-xs text-muted-foreground">Fully Indexed</div>
              </div>
              
              <div className="text-center p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
                <FileSearch className="h-6 w-6 mx-auto mb-2 text-blue-600" />
                <div className="text-2xl font-bold text-blue-600">{stats?.partially_indexed || 0}</div>
                <div className="text-xs text-muted-foreground">Partial</div>
              </div>
              
              <div className="text-center p-3 bg-red-50 dark:bg-red-950 rounded-lg">
                <AlertCircle className="h-6 w-6 mx-auto mb-2 text-red-600" />
                <div className="text-2xl font-bold text-red-600">{stats?.failed || 0}</div>
                <div className="text-xs text-muted-foreground">Failed</div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleTriggerOcr}
                disabled={triggering || (stats?.incoming || 0) === 0}
                className="flex items-center gap-1"
              >
                <Play className={`h-4 w-4 ${triggering ? 'animate-pulse' : ''}`} />
                {triggering ? 'Processing...' : 'Trigger OCR'}
              </Button>
              
              <Badge variant="secondary" className="text-xs">
                Total: {getTotalFiles()} files
              </Badge>
              
              {lastUpdated && (
                <Badge variant="outline" className="text-xs">
                  Updated: {lastUpdated.toLocaleTimeString()}
                </Badge>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
