"use client";

import { useEffect, useMemo, useState } from "react";
import { getAdminComplaints } from "@/lib/api-client";
import type { AdminComplaintListResponse, Complaint } from "@/lib/types";
import { ComplaintFilters, type ComplaintFilterState } from "@/components/admin/complaint-filters";
import { ComplaintTable } from "@/components/admin/complaint-table";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminComplaintsPage() {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<ComplaintFilterState>({
    search: "",
    category: "all",
    priority: "all",
    status: "all",
    locality: "all",
    language: "all",
    duplicate: "all"
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);
    getAdminComplaints({
      search: filters.search || undefined,
      category: filters.category === "all" ? undefined : filters.category,
      priority: filters.priority === "all" ? undefined : filters.priority,
      status: filters.status === "all" ? undefined : filters.status,
      locality: filters.locality === "all" ? undefined : filters.locality,
      language: filters.language === "all" ? undefined : filters.language,
      page,
      pageSize: 20
    })
      .then((data: AdminComplaintListResponse) => {
        if (!mounted) return;
        setComplaints(data.items);
        setTotal(data.total);
      })
      .catch((requestError) => {
        if (!mounted) return;
        setError(
          requestError instanceof Error
            ? requestError.message
            : "No complaint data is available yet."
        );
      })
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [filters, page]);

  const localities = useMemo(
    () => [
      "Kondapur",
      "Madhapur",
      "Gachibowli",
      "Ameerpet",
      "Kukatpally",
      "Charminar",
      "Jubilee Hills",
      "Hitech City",
      "Begumpet",
      "Secunderabad"
    ],
    []
  );

  return (
    <div className="space-y-6 p-6">
      <header>
        <h1 className="text-2xl font-bold">Complaints</h1>
        <p className="text-muted-foreground">
          Review, filter, assign, and update civic complaints.
        </p>
      </header>
      <ComplaintFilters value={filters} onChange={setFilters} localities={localities} />
      {error && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
          {error}
        </div>
      )}
      {loading ? <Skeleton className="h-80 w-full" /> : <ComplaintTable complaints={complaints} />}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Showing {complaints.length} of {total}
        </span>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((value) => Math.max(1, value - 1))}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            disabled={page * 20 >= total}
            onClick={() => setPage((value) => value + 1)}
          >
            Next
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setFilters({ ...filters, search: "" })}
          >
            Clear Search
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setPage(1);
              setFilters({
                search: "",
                category: "all",
                priority: "all",
                status: "all",
                locality: "all",
                language: "all",
                duplicate: "all"
              });
            }}
          >
            Reset Filters
          </Button>
        </div>
      </div>
    </div>
  );
}
