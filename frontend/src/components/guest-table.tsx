"use client";

import { useState } from "react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import type { Guest } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface GuestTableProps {
  guests: Guest[];
  onDeleted: () => void;
  onGeneratePdf: (id: string) => void;
}

export default function GuestTable({
  guests,
  onDeleted,
  onGeneratePdf,
}: GuestTableProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  async function handleDelete(id: string, name: string) {
    if (!confirm(`Delete guest "${name}"? This cannot be undone.`)) return;
    setDeletingId(id);
    try {
      await api.delete(`/api/guests/${id}`);
      toast.success("Guest deleted");
      onDeleted();
    } catch {
      toast.error("Failed to delete guest");
    } finally {
      setDeletingId(null);
    }
  }

  if (guests.length === 0) {
    return (
      <p className="text-muted-foreground py-8 text-center">
        No guests found. Add your first guest record.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b text-xs font-medium uppercase tracking-wider">
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">Nationality</th>
            <th className="px-4 py-3">Stay</th>
            <th className="px-4 py-3">Passport</th>
            <th className="px-4 py-3">PDF</th>
            <th className="px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {guests.map((guest) => (
            <tr key={guest.id} className="border-b">
              <td className="px-4 py-3 font-medium">
                {guest.first_name} {guest.last_name}
              </td>
              <td className="px-4 py-3">{guest.nationality}</td>
              <td className="px-4 py-3">
                {guest.stay_from} — {guest.stay_to}
              </td>
              <td className="px-4 py-3">{guest.passport_number}</td>
              <td className="px-4 py-3">
                {guest.pdf_generated_at ? (
                  <span className="text-green-600">Generated</span>
                ) : (
                  <span className="text-muted-foreground">—</span>
                )}
              </td>
              <td className="px-4 py-3">
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onGeneratePdf(guest.id)}
                  >
                    Generate PDF
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      handleDelete(
                        guest.id,
                        `${guest.first_name} ${guest.last_name}`,
                      )
                    }
                    disabled={deletingId === guest.id}
                  >
                    {deletingId === guest.id ? "Deleting..." : "Delete"}
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
