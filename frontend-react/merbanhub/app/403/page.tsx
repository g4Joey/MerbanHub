"use client";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function ForbiddenPage() {
  const router = useRouter();
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-3xl font-bold mb-4">403 - Forbidden</h1>
      <p className="mb-6">
        You cannot access this page since you are not an IT personnel.
      </p>
      <Button onClick={() => router.push("/login")}>Go to Login</Button>
    </div>
  );
}
