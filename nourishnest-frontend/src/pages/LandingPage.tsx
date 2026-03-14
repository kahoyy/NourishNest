import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  Sparkles,
  Package,
  Globe,
  Trophy,
  Check,
  Leaf,
  ChefHat,
  ArrowRight,
  ChartBar,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/context/AuthContext'
import { publicClient } from '@/lib/api/client'
import type { SubscriptionPlan } from '@/types/user.types'
import { queryKeys } from '@/lib/queryKeys'

function PublicNavbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex h-16 items-center justify-between bg-background/60 backdrop-blur-xl border-b border-border/40 px-6 md:px-12 transition-all duration-300">
      <div className="flex items-center gap-2 group cursor-pointer">
        <div className="bg-primary/10 p-1.5 rounded-lg group-hover:bg-primary/20 transition-colors">
          <Leaf className="h-5 w-5 text-primary" />
        </div>
        <span className="text-xl font-bold tracking-tight text-foreground">NourishNest</span>
      </div>
      <div className="flex items-center gap-4">
        <Link to="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-2">
          Log in
        </Link>
        <Button asChild className="rounded-full px-6 shadow-sm hover:shadow-md transition-all">
          <Link to="/register">Get Started</Link>
        </Button>
      </div>
    </nav>
  )
}

const features = [
  {
    icon: Sparkles,
    title: 'AI Recipe Generation',
    description: 'Transform your available ingredients into culinary masterpieces with personalized AI suggestions.',
    className: 'md:col-span-2 md:row-span-2 bg-gradient-to-br from-primary/5 to-transparent flex flex-col',
    visual: (
      <div className="flex flex-col gap-3 mt-8 w-full max-w-sm mx-auto flex-1 justify-center">
        <div className="bg-background rounded-lg p-3 shadow-sm border border-border/50 flex items-center gap-3 w-5/6 hover:shadow-md transition-shadow">
          <div className="bg-primary/20 p-2 rounded-full"><Sparkles className="w-4 h-4 text-primary" /></div>
          <div className="flex flex-col gap-1.5 w-full">
            <div className="h-2 bg-muted rounded-full w-3/4"></div>
            <div className="h-2 bg-muted rounded-full w-1/2"></div>
          </div>
        </div>
        <div className="bg-primary text-primary-foreground rounded-lg p-5 shadow-sm self-end w-5/6 ml-auto relative group overflow-hidden hover:shadow-md transition-shadow cursor-default">
            <div className="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
            <div className="font-semibold text-sm mb-3 relative z-10">Avocado Toast with Egg</div>
            <div className="flex gap-2 relative z-10">
               <Badge variant="secondary" className="bg-primary-foreground/20 hover:bg-primary-foreground/30 text-[10px] px-2 py-0 border-none text-primary-foreground rounded-md shadow-none pointer-events-none">15 mins</Badge>
               <Badge variant="secondary" className="bg-primary-foreground/20 hover:bg-primary-foreground/30 text-[10px] px-2 py-0 border-none text-primary-foreground rounded-md shadow-none pointer-events-none">Breakfast</Badge>
            </div>
        </div>
      </div>
    )
  },
  {
    icon: Package,
    title: 'Smart Pantry',
    description: 'Intelligent tracking with expiry alerts to dramatically reduce food waste.',
    className: 'md:col-span-1 md:row-span-1 flex flex-col',
    visual: (
      <div className="flex flex-col gap-2 mt-8 flex-1 w-full max-w-[250px] mx-auto justify-end pb-2">
        <div className="flex items-center justify-between p-2.5 rounded-md bg-background border border-border/50 shadow-sm border-l-4 border-l-destructive hover:scale-[1.02] transition-transform">
          <span className="text-sm font-medium">Whole Milk</span>
          <Badge variant="destructive" className="text-[10px] px-1.5 py-0 h-4 rounded shadow-none pointer-events-none">Exp Today</Badge>
        </div>
        <div className="flex items-center justify-between p-2.5 rounded-md bg-background border border-border/50 shadow-sm border-l-4 border-l-orange-500 hover:scale-[1.02] transition-transform delay-75">
          <span className="text-sm font-medium">Free Range Eggs</span>
          <span className="text-[10px] font-semibold text-orange-600 dark:text-orange-400">3 days</span>
        </div>
        <div className="flex items-center justify-between p-2.5 rounded-md bg-background border border-border/50 shadow-sm border-l-4 border-l-emerald-500 hover:scale-[1.02] transition-transform delay-150">
          <span className="text-sm font-medium">Sourdough Bread</span>
          <span className="text-[10px] font-medium text-emerald-600 dark:text-emerald-400">Good</span>
        </div>
      </div>
    )
  },
  {
    icon: Globe,
    title: 'Community',
    description: 'Fork, modify, and share recipes with home chefs globally.',
    className: 'md:col-span-1 md:row-span-1 flex flex-col overflow-hidden',
    visual: (
      <div className="flex gap-3 justify-center mt-6 h-full items-end pb-2 px-2">
        <div className="bg-background rounded-lg p-2.5 border border-border/50 flex-shrink-0 w-32 shadow-md relative -rotate-6 translate-y-4 z-10 hover:rotate-0 hover:translate-y-0 hover:z-20 transition-all cursor-pointer">
           <div className="h-16 w-full bg-muted rounded-md mb-2.5 flex items-center justify-center">
               <ChefHat className="w-6 h-6 text-muted-foreground/30" />
           </div>
           <div className="text-xs font-semibold truncate mb-1">Garlic Pasta</div>
           <div className="text-[10px] text-muted-foreground flex items-center gap-1"><Globe className="w-3 h-3"/> 24 forks</div>
        </div>
        <div className="bg-background rounded-lg p-2.5 border border-border/50 flex-shrink-0 w-32 shadow-sm relative rotate-3 translate-y-1 hover:rotate-0 hover:-translate-y-1 hover:shadow-md transition-all cursor-pointer">
           <div className="h-16 w-full bg-secondary rounded-md mb-2.5 flex items-center justify-center">
               <Leaf className="w-5 h-5 text-secondary-foreground/40" />
           </div>
           <div className="text-xs font-semibold truncate mb-1">Vegan Curry</div>
           <div className="text-[10px] text-muted-foreground flex items-center gap-1"><Globe className="w-3 h-3"/> 12 forks</div>
        </div>
      </div>
    )
  },
  {
    icon: Trophy,
    title: 'Gamified Kitchen',
    description: 'Build cooking streaks, earn badges, and level up your culinary skills.',
    className: 'md:col-span-2 md:row-span-1 bg-gradient-to-br from-emerald-50/50 to-transparent dark:from-emerald-950/20 flex flex-col',
    visual: (
      <div className="flex flex-col sm:flex-row items-center gap-6 mt-6 flex-1 justify-center w-full min-h-[120px]">
        <div className="flex-1 w-full max-w-[280px]">
           <div className="flex items-center gap-4 bg-background p-3.5 rounded-lg border border-border/50 shadow-sm hover:shadow-md transition-shadow">
            <div className="relative">
              <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center border-2 border-orange-500 shadow-inner">
                 <span className="text-xl">🔥</span>
              </div>
              <div className="absolute -bottom-1 -right-1 bg-orange-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-sm shadow-sm pointer-events-none">x5</div>
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-center mb-2">
                 <span className="text-sm font-bold">Level 4 Chef</span>
                 <span className="text-[10px] font-semibold text-muted-foreground bg-muted px-1.5 py-0.5 rounded-sm">850 / 1000 XP</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                 <div className="h-full bg-primary w-[85%] rounded-full transition-all duration-1000 ease-out"></div>
              </div>
            </div>
          </div>
        </div>
        <div className="flex gap-3 justify-center items-center">
           <div className="w-12 h-12 rounded-full bg-yellow-100 dark:bg-yellow-900/30 border-2 border-yellow-400 flex items-center justify-center shadow-md transform hover:scale-110 transition-transform cursor-help" title="First Recipe"><Trophy className="w-5 h-5 text-yellow-600 dark:text-yellow-400"/></div>
           <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 border-2 border-emerald-400 flex items-center justify-center shadow-md transform hover:scale-110 transition-transform cursor-help" title="Zero Waste Week"><Leaf className="w-5 h-5 text-emerald-600 dark:text-emerald-400"/></div>
           <div className="w-12 h-12 rounded-full bg-muted border-2 border-dashed border-border flex items-center justify-center opacity-60"><Trophy className="w-5 h-5 text-muted-foreground opacity-50"/></div>
        </div>
      </div>
    )
  },
]

const steps = [
  { num: '01', title: 'Inventory', desc: 'Scan or log your pantry items.' },
  { num: '02', title: 'Generative AI', desc: 'Get recipes based on what you have.' },
  { num: '03', title: 'Cook & Earn', desc: 'Log meals and build rewarding habits.' },
]

export function LandingPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading && isAuthenticated) navigate('/inventory')
  }, [isAuthenticated, isLoading, navigate])

  const { data: plans } = useQuery({
    queryKey: queryKeys.subscriptionPlans(),
    queryFn: async () => {
      const res = await publicClient.get('/subscription/plans/')
      return res.data as SubscriptionPlan[]
    },
  })

  if (isLoading) return null

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-primary/20 selection:text-primary pb-0">
      <PublicNavbar />

      {/* Hero */}
      <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 px-6 overflow-hidden flex flex-col items-center text-center">
        {/* Abstract Background Shapes */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-[500px] opacity-30 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-primary/30 rounded-full mix-blend-multiply filter blur-3xl animate-pulse" />
          <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-teal-200/40 rounded-full mix-blend-multiply filter blur-3xl animate-pulse delay-1000" />
        </div>

        <Badge variant="outline" className="mb-8 rounded-full px-4 py-1.5 border-primary/20 bg-primary/5 text-primary text-sm font-medium backdrop-blur-sm">
          <Sparkles className="w-4 h-4 mr-2 inline-block" />
          The future of home cooking
        </Badge>
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-foreground mb-8 max-w-4xl leading-[1.1]">
          Smart Kitchen Management, <br className="hidden md:block"/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-teal-400">Powered by AI</span>
        </h1>
        
        <p className="text-lg md:text-xl text-muted-foreground/90 max-w-2xl mb-12 leading-relaxed">
          Eliminate food waste, discover creative recipes from your existing pantry, and earn rewards for building sustainable cooking habits.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto z-10">
          <Button size="lg" className="rounded-full h-14 px-8 text-base shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 transition-all group" asChild>
            <Link to="/register">
              Start Free Trial 
              <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" className="rounded-full h-14 px-8 text-base border-border/60 hover:bg-muted/50 transition-colors" asChild>
            <Link to="/community">Explore Community</Link>
          </Button>
        </div>
      </section>

      {/* Features - Bento Box Style */}
      <section className="py-24 px-6 max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">Everything your kitchen needs</h2>
          <p className="text-muted-foreground text-lg max-w-xl mx-auto">A comprehensive suite of tools designed to make cooking effortless and enjoyable.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 md:grid-rows-2 gap-6">
          {features.map(({ icon: Icon, title, description, className, visual }) => (
            <Card key={title} className={`overflow-hidden border-border/50 shadow-sm hover:shadow-md transition-shadow group ${className}`}>
              <CardHeader className="h-full flex flex-col p-6 items-start">
                <div className="p-3 rounded-xl bg-background/50 backdrop-blur-sm border border-border/50 mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <div className="w-full">
                  <CardTitle className="text-xl mb-2">{title}</CardTitle>
                  <p className="text-base text-muted-foreground/80 leading-relaxed mt-1">
                    {description}
                  </p>
                </div>
                {visual}
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      {/* How It Works - Minimal Timeline */}
      <section className="py-24 px-6 bg-muted/30 border-y border-border/40">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-6">Effortless workflow</h2>
              <p className="text-lg text-muted-foreground mb-12">NourishNest learns from your habits and inventory to provide a seamless cooking experience.</p>
              
              <div className="space-y-8 relative before:absolute before:inset-0 before:ml-6 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border/60 before:to-transparent">
                {steps.map((step, idx) => (
                  <div key={idx} className="relative flex items-start gap-6">
                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-background border border-primary/30 flex items-center justify-center text-primary font-bold shadow-sm z-10 transition-transform hover:scale-110">
                      {step.num}
                    </div>
                    <div className="pt-2">
                      <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                      <p className="text-muted-foreground">{step.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative h-[400px] md:h-[500px] rounded-3xl overflow-hidden border border-border/50 bg-background/50 shadow-2xl flex items-center justify-center mx-4 md:mx-0">
              {/* Decorative mockup/illustration area */}
              <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 to-teal-500/5"></div>
              <div className="flex flex-col items-center justify-center space-y-4 animate-pulse">
                <div className="p-6 bg-background rounded-2xl shadow-sm border border-border/60">
                     <ChartBar className="w-16 h-16 text-primary/40" />
                </div>
                <div className="flex gap-2">
                    <div className="w-16 h-2 bg-primary/20 rounded-full"></div>
                    <div className="w-8 h-2 bg-primary/20 rounded-full"></div>
                </div>
                 <div className="w-32 h-2 bg-primary/20 rounded-full"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      {plans && plans.length > 0 && (
        <section className="py-24 px-6 max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">Simple, transparent pricing</h2>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto">Choose the perfect plan for your culinary journey.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center lg:px-12">
            {plans.map((plan) => (
              <Card
                key={plan.id}
                className={`relative flex flex-col h-full border-border/50 shadow-sm hover:shadow-xl transition-all duration-300 ${
                  plan.tier === 'premium' ? 'border-primary/50 shadow-primary/10 scale-100 md:scale-105 z-10' : ''
                }`}
              >
                {plan.tier === 'premium' && (
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-primary text-primary-foreground px-4 py-1 rounded-full text-xs font-bold uppercase tracking-wider shadow-sm">
                    Most Popular
                  </div>
                )}
                <CardHeader className="text-center pb-2">
                  <CardTitle className="text-xl text-muted-foreground font-medium">{plan.name}</CardTitle>
                  <div className="mt-4 flex items-baseline justify-center gap-x-2">
                    <span className="text-5xl font-bold tracking-tight text-foreground">
                      {plan.price === 0 ? 'Free' : `$${plan.price}`}
                    </span>
                    {plan.price > 0 && <span className="text-sm font-semibold leading-6 text-muted-foreground">/mo</span>}
                  </div>
                </CardHeader>
                <CardContent className="flex flex-col flex-1 justify-between pt-6">
                  <ul className="space-y-4 mb-8">
                    {plan.features.map((f, i) => (
                      <li key={i} className="flex gap-x-3 text-sm leading-6 text-muted-foreground">
                        <Check className="h-5 w-5 flex-none text-primary" aria-hidden="true" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <Button
                    className={`w-full rounded-full h-12 ${plan.tier === 'premium' ? 'hover:shadow-md' : 'bg-secondary/50 text-secondary-foreground hover:bg-secondary/80'}`}
                    variant={plan.tier === 'premium' ? 'default' : 'secondary'}
                    asChild
                  >
                    <Link to="/register">Get started today</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* CTA Banner */}
      <section className="relative py-24 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-primary/5" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-background" />
        <div className="relative max-w-3xl mx-auto text-center z-10">
          <div className="inline-flex items-center justify-center p-5 rounded-full bg-primary/10 text-primary mb-8 animate-bounce">
            <ChefHat className="h-10 w-10" />
          </div>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">Ready to transform your kitchen?</h2>
          <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
            Join thousands of home chefs cooking smarter, reducing waste, and enjoying delicious meals.
          </p>
          <Button size="lg" className="rounded-full h-14 px-10 text-lg shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all" asChild>
            <Link to="/register">Create Your Free Account</Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/40 bg-background pt-16 pb-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col items-center">
          <div className="flex items-center gap-2 mb-8 group cursor-pointer">
            <Leaf className="h-5 w-5 text-primary group-hover:rotate-12 transition-transform" />
            <span className="font-bold text-lg tracking-tight">NourishNest</span>
          </div>
          <div className="flex flex-wrap justify-center gap-x-8 gap-y-4 mb-12 text-sm font-medium text-muted-foreground">
            <Link to="/login" className="hover:text-foreground transition-colors">Log in</Link>
            <Link to="/register" className="hover:text-foreground transition-colors">Sign up</Link>
            <Link to="/community" className="hover:text-foreground transition-colors">Community</Link>
            <Link to="#" className="hover:text-foreground transition-colors">Privacy Policy</Link>
            <Link to="#" className="hover:text-foreground transition-colors">Terms of Service</Link>
          </div>
          <p className="text-sm text-muted-foreground/60 text-center">
            &copy; {new Date().getFullYear()} NourishNest. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}
