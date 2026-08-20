import React from "react";
import { motion, useScroll, useTransform } from "framer-motion";

export default function Background() {
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 1200], [0, 180]);
  const y2 = useTransform(scrollY, [0, 1200], [0, -120]);

  return (
    <div className="background" aria-hidden="true">
      <motion.div className="orb orb-a" style={{ y: y1 }} />
      <motion.div className="orb orb-b" style={{ y: y2 }} />
      <div className="grid-overlay" />
      <div className="noise-overlay" />
    </div>
  );
}
