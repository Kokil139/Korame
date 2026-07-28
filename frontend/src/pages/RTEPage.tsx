import React, { useState } from "react";
import { submitBusinessRequirement } from "../api/chatApi";

type Message = {
  id: string;
  role: "user" | "rte" | "system";
  text: string;
};

const RTEPage: React.FC = () => {
  const [requirement, setRequirement] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e?: React.FormEvent<HTMLFormElement | HTMLButtonElement>) => {
    e?.preventDefault();
    setError(null);
    if (!requirement.trim()) return;
    const userMsg: Message = {
      id: String(Date.now()),
      role: "user",
      text: requirement.trim(),
    };
    setMessages((m: Message[]) => [...m, userMsg]);
    setLoading(true);
    try {
      const payload = { requirement: requirement.trim() };
      const data = await submitBusinessRequirement(payload);
      // Expecting backend to return { messages: [{ role, text }] } or { questions: [...] }
      if (data?.messages && Array.isArray(data.messages)) {
        const newMsgs = data.messages.map((msg: any, idx: number) => ({
          id: `srv-${Date.now()}-${idx}`,
          role: msg.role || "rte",
          text: msg.text || String(msg),
        }));
        setMessages((m: Message[]) => [...m, ...newMsgs]);
      } else if (data?.questions && Array.isArray(data.questions)) {
        const qMsgs = data.questions.map((q: any, idx: number) => ({
          id: `q-${Date.now()}-${idx}`,
          role: "rte",
          text: q,
        }));
        setMessages((m: Message[]) => [...m, ...qMsgs]);
      } else if (typeof data === "string") {
          setMessages((m: Message[]) => [
              ...m,
              { id: `srv-${Date.now()}`, role: "rte", text: data },
            ]);
      } else {
        setMessages((m: Message[]) => [
          ...m,
          { id: `srv-${Date.now()}`, role: "rte", text: "No response from RTE agent." },
        ]);
      }
      setRequirement("");
    } catch (err: any) {
      setError(err?.message || "Failed to send requirement");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>RTE - Business Requirement</h2>
      <p>Provide your business requirement below. The RTE agent will reply and may ask clarifying questions.</p>

      <form onSubmit={onSubmit} style={{ marginBottom: 12 }}>
        <div>
          <textarea
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            rows={6}
            style={{ width: "100%", padding: 8 }}
            placeholder="Describe the business requirement..."
            disabled={loading}
          />
        </div>
        <div style={{ marginTop: 8 }}>
          <button type="submit" onClick={onSubmit} disabled={loading}>
            {loading ? "Sending..." : "Submit Requirement"}
          </button>
        </div>
      </form>

      {error && <div style={{ color: "red" }}>Error: {error}</div>}

      <div>
        <h3>Conversation</h3>
        <div style={{ border: "1px solid #ddd", padding: 12, minHeight: 120 }}>
          {messages.length === 0 && <div style={{ color: "#666" }}>No messages yet.</div>}
          {messages.map((m) => (
            <div key={m.id} style={{ marginBottom: 8 }}>
              <strong>{m.role === "user" ? "You" : m.role === "rte" ? "RTE" : "System"}:</strong>
              <div>{m.text}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RTEPage;


