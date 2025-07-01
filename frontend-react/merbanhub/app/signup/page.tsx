import { GalleryVerticalEnd } from "lucide-react"
import logo from "@/components/assets/merbanhub.jpg"
import Image from "next/image"
import { LoginForm } from "@/components/login-form"
import { SignUp } from "@/components/signup-form"
import laptop from "@/components/assets/laptop.jpg"

export default function SignUPage() {
  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <a href="#" className="flex items-center gap-2 font-medium">
            <Image
              src={logo}
              alt="MerbanHub Logo"
              className="ml-2 h-[10rem] w-[10rem] rounded-full"
            />
          </a>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-xs">
            <SignUp />
          </div>
        </div>
      </div>
      <div className="bg-muted relative hidden lg:block">
        <Image
          src={laptop}
          alt="Image"
          className="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
        />
      </div>
    </div>
  );
}
