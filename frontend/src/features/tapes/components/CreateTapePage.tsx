import { useState } from "react";
import type { CassetteStyle, CreateTapeRequest, Tape } from "../types";
import { useMutation } from "@tanstack/react-query";
import { tapesApi } from "../api/tapesApi";
import { useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import { getErrorMessage } from "@/api/errorMessage";

export function CreateTapePage() {
  const [formData, setFormData] = useState<CreateTapeRequest>({
    title: "",
    cassette_style: "classic",
    length_minutes: 60,
  });
  const navigate = useNavigate();
  const { mutate, isPending } = useMutation<Tape, Error, CreateTapeRequest>({
    mutationFn: (data) => tapesApi.createTape(data),
    onSuccess: (tape) => {
      navigate(`/tapes/${tape.id}`);
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, "Failed to create tape."));
    },
  });
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-6">Create a Tape</h1>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutate(formData);
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) =>
                setFormData({ ...formData, title: e.target.value })
              }
              className="w-full border rounded px-3 py-2 text-sm"
              placeholder="e.g. Summer Mix"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Style</label>
            <select
              value={formData.cassette_style}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  cassette_style: e.target.value as CassetteStyle,
                })
              }
              className="w-full border rounded px-3 py-2 text-sm"
            >
              <option value="classic">Classic</option>
              <option value="chrome">Chrome</option>
              <option value="metal">Metal</option>
              <option value="vintage">Vintage</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Length</label>
            <select
              value={formData.length_minutes}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  length_minutes: Number(e.target.value),
                })
              }
              className="w-full border rounded px-3 py-2 text-sm"
            >
              <option value={60}>60 minutes</option>
              <option value={90}>90 minutes</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={isPending}
            className="w-full bg-blue-600 text-white py-2 rounded font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {isPending ? "Creating..." : "Create Tape"}
          </button>
        </form>
      </div>
    </div>
  );
}
