"use client";

import React from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { History, X, Clock, BarChart3 } from "lucide-react";
import { useSignalHistory } from "@/contexts/signal-history-context";
import { JobStatus } from "@/lib/types";

interface SignalHistorySidebarProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHour = Math.floor(diffMin / 60);
  if (diffHour < 24) return `${diffHour}h ago`;
  const diffDay = Math.floor(diffHour / 24);
  return `${diffDay}d ago`;
}

function statusBadgeVariant(status: JobStatus): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "completed":
      return "default";
    case "processing":
      return "secondary";
    case "failed":
      return "destructive";
    default:
      return "outline";
  }
}

export function SignalHistorySidebar({
  open,
  onOpenChange,
}: SignalHistorySidebarProps) {
  const { state, setActive, removeEntry } = useSignalHistory();

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="w-[340px] sm:w-[380px] p-0">
        <SheetHeader className="px-4 pt-4 pb-2">
          <SheetTitle className="flex items-center gap-2 text-base">
            <History className="h-4 w-4" />
            Signal History
          </SheetTitle>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-80px)] px-4 pb-4">
          {state.entries.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <BarChart3 className="h-10 w-10 mb-3 opacity-50" />
              <p className="text-sm">No signals in history.</p>
              <p className="text-xs mt-1">Upload a CSV to get started.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {state.entries.map((entry) => {
                const isActive = state.activeJobId === entry.jobId;
                return (
                  <button
                    key={entry.jobId}
                    onClick={() => {
                      setActive(entry.jobId);
                      onOpenChange(false);
                    }}
                    className={`w-full text-left rounded-lg border p-3 transition-colors hover:bg-accent ${
                      isActive
                        ? "border-primary bg-primary/5"
                        : "border-border bg-card"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium truncate">
                          {entry.signalName}
                        </p>
                        <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          <span>{formatRelativeTime(entry.uploadedAt)}</span>
                        </div>
                        <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                          <span>
                            ctx={entry.config.context_size} pred=
                            {entry.config.prediction_length}
                          </span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        <Badge
                          variant={statusBadgeVariant(entry.status)}
                          className="text-[10px] px-1.5 py-0"
                        >
                          {entry.status}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 text-muted-foreground hover:text-destructive"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeEntry(entry.jobId);
                          }}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
