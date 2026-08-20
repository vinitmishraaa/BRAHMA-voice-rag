import React from "react";

import {
  Database,
  FileSearch,
  Mic2,
  Search,
  Languages,
} from "lucide-react";

import { motion } from "framer-motion";


const stages = [
  [
    "01",
    "Voice",
    "Sarvam STT",
    Mic2,
  ],
  [
    "02",
    "Language",
    "Language routing",
    Languages,
  ],
  [
    "03",
    "Retrieve",
    "Qdrant search",
    Database,
  ],
  [
    "04",
    "Ground",
    "Relevant context",
    FileSearch,
  ],
  [
    "05",
    "Answer",
    "Extractive answer",
    Search,
  ],
];


export default function Pipeline() {
  return (
    <section
      id="pipeline"
      className="pipeline-section"
    >
      <div className="section-heading">

        <div>
          <div className="section-kicker">
            UNDER THE HOOD
          </div>

          <h2>
            From voice to grounded
            answer.
          </h2>
        </div>

        <p>
          Every response travels
          through a measurable
          retrieval pipeline.
        </p>

      </div>


      <div className="pipeline">

        {stages.map(
          (
            [
              number,
              title,
              subtitle,
              Icon,
            ],
            index
          ) => (
            <motion.div
              className="pipeline-card"
              key={number}
              initial={{
                opacity: 0,
                y: 24,
              }}
              whileInView={{
                opacity: 1,
                y: 0,
              }}
              viewport={{
                once: true,
                amount: 0.25,
              }}
              transition={{
                duration: 0.5,
                delay:
                  index * 0.08,
              }}
            >
              <span>
                {number}
              </span>

              <Icon size={22} />

              <h3>
                {title}
              </h3>

              <p>
                {subtitle}
              </p>
            </motion.div>
          )
        )}

      </div>
    </section>
  );
}