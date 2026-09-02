import { routes, type VercelConfig } from "@vercel/config/v1";

const BACKEND_URL = process.env.BACKEND_URL || "";

export const config: VercelConfig = {
  rewrites: [
    routes.rewrite("/api/:path*", `${BACKEND_URL}/api/:path*`),
    routes.rewrite(
      "/((?!favicon.svg|cassette.png|icons.svg|assets).*)",
      "/index.html",
    ),
  ],
};
