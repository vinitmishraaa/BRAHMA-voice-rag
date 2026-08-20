import React, {
  useState,
} from "react";

import {
  Bot,
  Copy,
  Check,
} from "lucide-react";

import { motion } from "framer-motion";

import SourceList from "./SourceList";


export default function AnswerPanel({
  answer,
  sources,
}) {
  const [
    copied,
    setCopied,
  ] = useState(false);


  if (!answer) {
    return (
      <div className="empty-answer">

        <Bot size={25} />

        <div>
          <strong>
            Your grounded answer
            will appear here.
          </strong>

          <p>
            Choose a microphone,
            record a question, or
            type a question to query
            the retrieval pipeline.
          </p>
        </div>

      </div>
    );
  }


  async function copyAnswer() {
    try {
      await navigator.clipboard.writeText(
        answer
      );

      setCopied(true);

      window.setTimeout(
        () => setCopied(false),
        1400
      );
    } catch {
      setCopied(false);
    }
  }


  return (
    <motion.div
      className="answer-panel"
      initial={{
        opacity: 0,
        y: 16,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
    >

      <div className="answer-head">

        <div className="answer-title">
          <Bot size={19} />
          BRAHMA
        </div>

        <div className="answer-actions">

          <button
            className="icon-button"
            onClick={
              copyAnswer
            }
            title="Copy answer"
          >
            {copied ? (
              <Check size={16} />
            ) : (
              <Copy size={16} />
            )}
          </button>

        </div>

      </div>


      <div className="answer-text">
        {answer}
      </div>


      <SourceList
        sources={sources}
      />

    </motion.div>
  );
}