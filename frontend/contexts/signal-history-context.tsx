"use client";

import React, {
  createContext,
  useContext,
  useReducer,
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import {
  getJobList,
  getJobResult,
  getJobOriginalData,
  reapplyJob as reapplyJobApi,
} from "@/lib/api";
import {
  HistoryEntry,
  PredictionConfig,
  JobStatus,
} from "@/lib/types";
import { buildChartData } from "@/lib/chart-data";
import { ChartData } from "@/lib/chart-types";

/* ------------------------------------------------------------------ */
/*  State                                                              */
/* ------------------------------------------------------------------ */

interface HistoryState {
  entries: HistoryEntry[];
  activeJobId: string | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: HistoryState = {
  entries: [],
  activeJobId: null,
  isLoading: false,
  error: null,
};

/* ------------------------------------------------------------------ */
/*  Actions                                                            */
/* ------------------------------------------------------------------ */

type HistoryAction =
  | { type: "SET_ENTRIES"; entries: HistoryEntry[] }
  | { type: "ADD_ENTRY"; entry: HistoryEntry }
  | { type: "UPDATE_STATUS"; jobId: string; status: JobStatus }
  | { type: "SET_ACTIVE"; jobId: string | null }
  | { type: "REMOVE_ENTRY"; jobId: string }
  | { type: "SET_LOADING"; isLoading: boolean }
  | { type: "SET_ERROR"; error: string | null };

/* ------------------------------------------------------------------ */
/*  Reducer                                                            */
/* ------------------------------------------------------------------ */

function historyReducer(
  state: HistoryState,
  action: HistoryAction
): HistoryState {
  switch (action.type) {
    case "SET_ENTRIES":
      return { ...state, entries: action.entries };
    case "ADD_ENTRY":
      return { ...state, entries: [action.entry, ...state.entries] };
    case "UPDATE_STATUS":
      return {
        ...state,
        entries: state.entries.map((e) =>
          e.jobId === action.jobId ? { ...e, status: action.status } : e
        ),
      };
    case "SET_ACTIVE":
      return { ...state, activeJobId: action.jobId };
    case "REMOVE_ENTRY":
      return {
        ...state,
        entries: state.entries.filter((e) => e.jobId !== action.jobId),
        activeJobId:
          state.activeJobId === action.jobId ? null : state.activeJobId,
      };
    case "SET_LOADING":
      return { ...state, isLoading: action.isLoading };
    case "SET_ERROR":
      return { ...state, error: action.error };
    default:
      return state;
  }
}

/* ------------------------------------------------------------------ */
/*  Context value                                                      */
/* ------------------------------------------------------------------ */

interface HistoryContextValue {
  state: HistoryState;
  activeChartData: ChartData | null;
  activeOriginalData: number[];
  addEntry: (entry: HistoryEntry) => void;
  removeEntry: (jobId: string) => void;
  setActive: (jobId: string) => void;
  reapplyConfig: (jobId: string, config: PredictionConfig) => Promise<void>;
  loadHistory: () => Promise<void>;
}

const HistoryContext = createContext<HistoryContextValue | null>(null);

/* ------------------------------------------------------------------ */
/*  Provider                                                           */
/* ------------------------------------------------------------------ */

export function SignalHistoryProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(historyReducer, initialState);
  const [activeChartData, setActiveChartData] = useState<ChartData | null>(null);
  const [activeOriginalData, setActiveOriginalData] = useState<number[]>([]);

  /* ---- Load history from backend on mount ---- */
  const loadHistory = useCallback(async () => {
    dispatch({ type: "SET_LOADING", isLoading: true });
    try {
      const jobs = await getJobList();
      const entries: HistoryEntry[] = jobs.map((j) => ({
        jobId: j.job_id,
        signalName: j.signal_name || "Unnamed signal",
        uploadedAt: j.created_at,
        config: j.config || {
          context_size: 512,
          prediction_length: 96,
          frequency: "auto",
        },
        status: j.status as JobStatus,
      }));
      dispatch({ type: "SET_ENTRIES", entries });
    } catch (err) {
      dispatch({
        type: "SET_ERROR",
        error: err instanceof Error ? err.message : "Failed to load history",
      });
    } finally {
      dispatch({ type: "SET_LOADING", isLoading: false });
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  /* ---- Fetch data when active entry changes ---- */
  useEffect(() => {
    if (!state.activeJobId) {
      setActiveChartData(null);
      setActiveOriginalData([]);
      return;
    }

    let cancelled = false;

    async function loadActiveData() {
      try {
        const [dataRes, resultRes] = await Promise.all([
          getJobOriginalData(state.activeJobId!),
          getJobResult(state.activeJobId!),
        ]);

        if (cancelled) return;

        setActiveOriginalData(dataRes.data);

        if (
          resultRes.status === "completed" &&
          resultRes.forecast &&
          resultRes.metadata
        ) {
          const chartData = buildChartData(
            dataRes.data,
            resultRes.forecast,
            resultRes.metadata
          );
          setActiveChartData(chartData);
        } else {
          setActiveChartData(null);
        }
      } catch {
        if (!cancelled) setActiveChartData(null);
      }
    }

    loadActiveData();
    return () => {
      cancelled = true;
    };
  }, [state.activeJobId]);

  const addEntry = useCallback((entry: HistoryEntry) => {
    dispatch({ type: "ADD_ENTRY", entry });
  }, []);

  const removeEntry = useCallback((jobId: string) => {
    dispatch({ type: "REMOVE_ENTRY", jobId });
  }, []);

  const setActive = useCallback((jobId: string) => {
    dispatch({ type: "SET_ACTIVE", jobId });
  }, []);

  const reapplyConfig = useCallback(
    async (jobId: string, config: PredictionConfig) => {
      dispatch({ type: "SET_LOADING", isLoading: true });
      try {
        const response = await reapplyJobApi(jobId, {
          context_size: config.context_size || 512,
          prediction_length: config.prediction_length || 96,
          frequency: config.frequency || "auto",
        });

        const existing = state.entries.find((e) => e.jobId === jobId);

        const newEntry: HistoryEntry = {
          jobId: response.job_id,
          signalName: existing?.signalName || "Re-applied signal",
          uploadedAt: new Date().toISOString(),
          config,
          status: "processing",
        };

        dispatch({ type: "ADD_ENTRY", entry: newEntry });
        dispatch({ type: "SET_ACTIVE", jobId: response.job_id });
      } catch (err) {
        dispatch({
          type: "SET_ERROR",
          error: err instanceof Error ? err.message : "Re-apply failed",
        });
      } finally {
        dispatch({ type: "SET_LOADING", isLoading: false });
      }
    },
    [state.entries]
  );

  return (
    <HistoryContext.Provider
      value={{
        state,
        activeChartData,
        activeOriginalData,
        addEntry,
        removeEntry,
        setActive,
        reapplyConfig,
        loadHistory,
      }}
    >
      {children}
    </HistoryContext.Provider>
  );
}

/* ------------------------------------------------------------------ */
/*  Hook                                                               */
/* ------------------------------------------------------------------ */

export function useSignalHistory() {
  const context = useContext(HistoryContext);
  if (!context) {
    throw new Error(
      "useSignalHistory must be used within SignalHistoryProvider"
    );
  }
  return context;
}
