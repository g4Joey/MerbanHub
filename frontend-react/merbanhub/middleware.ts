import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;

  // Redirect root to login
  if (path === "/") {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Check if it's a protected route (all dashboard routes)
  if (path.startsWith("/dashboard")) {
    // Get the token from cookies
    const token = request.cookies.get("authToken")?.value;
    const userRole = request.cookies.get("userRole")?.value;

    // If no token, redirect to login
    if (!token) {
      return NextResponse.redirect(new URL("/login", request.url));
    }

    // If not admin and trying to access restricted routes
    if (
      userRole !== "ROLE_ADMIN" &&
      (path === "/dashboard/upload" || path === "/dashboard")
    ) {
      return NextResponse.redirect(new URL("/403", request.url));
    }
  }

  return NextResponse.next();
}

// Configure which paths middleware will run on
export const config = {
  matcher: ["/dashboard/:path*"],
};
