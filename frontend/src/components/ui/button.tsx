import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  // Base styles — consistent with existing CareerPilot btn system
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-xs font-bold transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#FF5722] focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        default:
          "bg-[#FF5722] text-white shadow hover:bg-[#E64A19] border border-[#FF5722] hover:border-[#E64A19]",
        destructive:
          "bg-red-600 text-white shadow hover:bg-red-700",
        outline:
          "border border-app bg-surface text-app hover:bg-subtle hover:text-app shadow-xs",
        secondary:
          "bg-subtle text-app border border-app hover:border-[#FF5722] hover:text-[#FF5722] dark:hover:text-[#FF7043]",
        ghost:
          "text-secondary hover:bg-subtle hover:text-app",
        link:
          "text-[#FF5722] dark:text-[#FF7043] underline-offset-4 hover:underline",
        glass:
          "bg-white/10 hover:bg-white/20 text-white border border-white/20 hover:border-white/40 backdrop-blur-sm",
      },
      size: {
        default: "h-9 px-5 py-2",
        sm: "h-7 px-3 py-1.5 text-[11px]",
        lg: "h-11 px-7 py-2.5 text-sm",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
