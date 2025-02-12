import Navigation from "@/components/Navigation";
import Hero from "@/components/Hero";
import Features from "@/components/Features";

export default function Home() {
  return (
    <>
      <Navigation />
      <main>
        <Hero />
        <Features />
      </main>
    </>
  );
}