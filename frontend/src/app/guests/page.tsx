"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { toast } from "sonner";
import { api, isAuthenticated } from "@/lib/api";
import type { GuestListResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import GuestTable from "@/components/guest-table";

export default function GuestListPage() {
  const router = useRouter();
  const [data, setData] = useState<GuestListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const pageSize = 20;

  // Filters
  const [search, setSearch] = useState("");
  const [nationality, setNationality] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  const fetchGuests = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        size: String(pageSize),
      });
      if (search) params.set("search", search);
      if (nationality) params.set("nationality", nationality);
      if (dateFrom) params.set("date_from", dateFrom);
      if (dateTo) params.set("date_to", dateTo);

      const result = await api.get<GuestListResponse>(
        `/api/guests?${params.toString()}`,
      );
      setData(result);
    } catch {
      // 401 handled by api client
    } finally {
      setLoading(false);
    }
  }, [page, search, nationality, dateFrom, dateTo]);

  useEffect(() => {
    fetchGuests();
  }, [fetchGuests]);

  function handleSearchChange(value: string) {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSearch(value);
      setPage(1);
    }, 300);
  }

  async function handleGeneratePdf(id: string) {
    try {
      await api.post(`/api/guests/${id}/pdf`, {});
      toast.success("PDF generated and uploaded to Google Drive");
      fetchGuests();
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Failed to generate PDF");
    }
  }

  const totalPages = data ? Math.ceil(data.total / pageSize) : 0;

  return (
    <div className="mx-auto w-full max-w-5xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Guest Records</h1>
        <Link href="/guests/new">
          <Button>+ New Guest</Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div className="min-w-[200px] flex-1">
          <label className="mb-1 block text-xs font-medium">Search name</label>
          <Input
            placeholder="Search by name..."
            defaultValue={search}
            onChange={(e) => handleSearchChange(e.target.value)}
          />
        </div>
        <div className="w-[160px]">
          <label className="mb-1 block text-xs font-medium">Nationality</label>
          <Input
            placeholder="e.g. British"
            value={nationality}
            onChange={(e) => {
              setNationality(e.target.value);
              setPage(1);
            }}
          />
        </div>
        <div className="w-[150px]">
          <label className="mb-1 block text-xs font-medium">Stay from</label>
          <Input
            type="date"
            value={dateFrom}
            onChange={(e) => {
              setDateFrom(e.target.value);
              setPage(1);
            }}
          />
        </div>
        <div className="w-[150px]">
          <label className="mb-1 block text-xs font-medium">Stay to</label>
          <Input
            type="date"
            value={dateTo}
            onChange={(e) => {
              setDateTo(e.target.value);
              setPage(1);
            }}
          />
        </div>
        {(search || nationality || dateFrom || dateTo) && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setSearch("");
              setNationality("");
              setDateFrom("");
              setDateTo("");
              setPage(1);
            }}
          >
            Clear
          </Button>
        )}
      </div>

      {loading ? (
        <p className="text-muted-foreground py-8 text-center">Loading...</p>
      ) : data ? (
        <>
          <GuestTable
            guests={data.items}
            onDeleted={fetchGuests}
            onGeneratePdf={handleGeneratePdf}
          />

          {totalPages > 1 && (
            <div className="mt-4 flex items-center justify-center gap-4">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <span className="text-sm">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}
