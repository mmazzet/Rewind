import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { tapesApi } from "../api/tapesApi";
import type { SendTapeRequest, SendTapeResponse } from "../types";
import { toast } from "react-hot-toast";
import { getErrorMessage } from "@/api/errorMessage";

interface SendTapeModalProps {
  tapeId: number;
  onClose: () => void;
}

export function SendTapeModal({ tapeId, onClose }: SendTapeModalProps) {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [sentTape, setSentTape] = useState<SendTapeResponse | null>(null);

  const { mutate: sendTape, isPending } = useMutation({
    mutationFn: (data: SendTapeRequest) => tapesApi.sendTape(tapeId, data),
    onSuccess: (data) => {
      setSentTape(data);
    },
    onError: (error: any) => {
      const details = error?.response?.data?.details;
      if (details?.recipient_email) {
        toast.error("Please enter a valid email address.");
      } else {
        toast.error(getErrorMessage(error, "Failed to send tape."));
      }
    },
  });

  function handleSubmit() {
    if (!email) return;
    sendTape({ recipient_email: email, message: message || undefined });
  }

  function handleCopyLink() {
    const url = `${window.location.origin}/tape/${sentTape?.public_token}`;
    navigator.clipboard.writeText(url);
    toast.success("Link copied!");
  }

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50"
      style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
    >
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        {sentTape ? (
          // Success state — show the public link
          <div>
            <h2 className="text-xl font-bold mb-2">Tape sent!</h2>
            <p className="text-sm text-gray-500 mb-4">
              Share this link with your friend:
            </p>
            <p className="text-sm font-mono bg-gray-100 rounded p-2 break-all mb-4">
              {window.location.origin}/tape/{sentTape.public_token}
            </p>
            <button
              onClick={handleCopyLink}
              className="w-full py-2 px-4 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors mb-2"
            >
              Copy link
            </button>
            <button
              onClick={onClose}
              className="w-full py-2 px-4 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors"
            >
              Close
            </button>
          </div>
        ) : (
          // Form state
          <div>
            <h2 className="text-xl font-bold mb-6">Send your tape</h2>

            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recipient email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="friend@example.com"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message (optional)
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Made this for you..."
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-6 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            <button
              onClick={handleSubmit}
              disabled={!email || isPending}
              className="w-full py-2 px-4 bg-green-600 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-green-700 transition-colors mb-2"
            >
              {isPending ? "Sending..." : "Send tape"}
            </button>
            <button
              onClick={onClose}
              className="w-full py-2 px-4 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
