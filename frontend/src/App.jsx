import React, {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ArrowDown,
  ArrowUpRight,
  Github,
  Instagram,
  LoaderCircle,
  Send,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { motion } from "framer-motion";

import Background from "./components/Background";
import Navbar from "./components/Navbar";
import MicSelector from "./components/MicSelector";
import VoiceButton from "./components/VoiceButton";
import LatencyBadge from "./components/LatencyBadge";
import AnswerPanel from "./components/AnswerPanel";
import Pipeline from "./components/Pipeline";

import {
  askRag,
  checkHealth,
  transcribeAudio,
} from "./api";

import {
  useMicrophone,
} from "./hooks/useMicrophone";


function formatTime(ms) {
  return `${(
    ms / 1000
  ).toFixed(1)}s`;
}


export default function App() {
  const mic =
    useMicrophone();

  const [
    backendOnline,
    setBackendOnline,
  ] = useState(false);

  const [
    question,
    setQuestion,
  ] = useState("");

  const [
    answer,
    setAnswer,
  ] = useState("");

  const [
    sources,
    setSources,
  ] = useState([]);

  const [
    latency,
    setLatency,
  ] = useState(null);

  const [
    busy,
    setBusy,
  ] = useState(false);

  const [
    stage,
    setStage,
  ] = useState("idle");

  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {
    checkHealth()
      .then(() =>
        setBackendOnline(true)
      )
      .catch(() =>
        setBackendOnline(false)
      );
  }, []);


  const recordingLabel =
    useMemo(
      () =>
        mic.recording
          ? `Listening · ${formatTime(
              mic.elapsedMs
            )}`
          : "Tap to speak",
      [
        mic.recording,
        mic.elapsedMs,
      ]
    );


  async function processQuestion(
    text
  ) {
    const clean =
      text.trim();

    if (!clean) {
      return;
    }

    setError("");
    setBusy(true);
    setStage("retrieving");

    try {
      const result =
        await askRag(clean);

      setQuestion(clean);

      setAnswer(
        result.answer ||
          ""
      );

      setSources(
        result.sources ||
          []
      );

      const totalLatency =
        result.latency?.total_ms ??
        null;

      setLatency(
        totalLatency
      );

      setBackendOnline(true);
      setStage("complete");

    } catch (err) {
      setError(
        err.message ||
          "Could not get a response from the backend."
      );

      setBackendOnline(false);
      setStage("error");

    } finally {
      setBusy(false);
    }
  }


  async function handleStop() {
    setStage(
      "transcribing"
    );

    setBusy(true);
    setError("");

    try {
      const blob =
        await mic.stop();

      if (!blob) {
        throw new Error(
          "No audio was captured. Please try again."
        );
      }

      const result =
        await transcribeAudio(
          blob,
          mic.selectedDeviceId
        );

      const text =
        result.text ||
        result.transcript ||
        "";

      if (!text.trim()) {
        throw new Error(
          "The speech-to-text service returned an empty transcript."
        );
      }

      setQuestion(
        text
      );

      await processQuestion(
        text
      );

    } catch (err) {
      setBusy(false);
      setStage("error");

      setError(
        err.message ||
          "Transcription failed."
      );
    }
  }


  async function submitText(
    event
  ) {
    event.preventDefault();

    await processQuestion(
      question
    );
  }


  return (
    <div
      id="top"
      className="app"
    >
      <Background />

      <Navbar
        backendOnline={
          backendOnline
        }
      />

      <main>

        <section
          className="hero container"
        >
          <motion.div
            className="hero-copy"
            initial={{
              opacity: 0,
              y: 30,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              duration: 0.7,
            }}
          >
            <div className="eyebrow">
              <span />
              VOICE-FIRST RETRIEVAL
            </div>

            <h1>
              Ask naturally.
              <br />
              <span>
                Retrieve intelligently.
              </span>
            </h1>

            <p>
              A voice-native RAG
              interface that turns
              spoken questions into
              grounded, measurable
              answers.
            </p>

            <div className="hero-meta">
              <span>
                <ShieldCheck
                  size={15}
                />
                Grounded responses
              </span>

              <span>
                <Sparkles
                  size={15}
                />
                Low-friction UX
              </span>

              <span>
                <ArrowDown
                  size={15}
                />
                Scroll to explore
              </span>
            </div>
          </motion.div>


          <motion.div
            className="hero-orbit"
            initial={{
              opacity: 0,
              scale: 0.85,
            }}
            animate={{
              opacity: 1,
              scale: 1,
            }}
            transition={{
              duration: 0.9,
              delay: 0.15,
            }}
          >
            <div className="orbit orbit-1" />
            <div className="orbit orbit-2" />

            <div className="core">
              <MicSelector
                {...mic}
              />

              <div className="core-label">
                VOICE RAG
              </div>
            </div>
          </motion.div>
        </section>


        <section
          id="console"
          className="console-section container"
        >
          <div className="console-grid">

            <div className="control-card glass">

              <div className="card-top">
                <div>
                  <div className="section-kicker">
                    VOICE CONSOLE
                  </div>

                  <h2>
                    Speak your question.
                  </h2>
                </div>

                <div
                  className={`stage-pill ${stage}`}
                >
                  {stage}
                </div>
              </div>


              <MicSelector
                devices={
                  mic.devices
                }
                selectedDeviceId={
                  mic.selectedDeviceId
                }
                setSelectedDeviceId={
                  mic.setSelectedDeviceId
                }
                refreshDevices={
                  mic.refreshDevices
                }
              />


              <div className="voice-area">

                <VoiceButton
                  recording={
                    mic.recording
                  }
                  onStart={
                    mic.start
                  }
                  onStop={
                    handleStop
                  }
                  disabled={
                    busy
                  }
                />

                <div className="recording-label">
                  {recordingLabel}
                </div>

                {mic.permission ===
                  "denied" && (
                  <small className="hint">
                    Allow microphone
                    access in your
                    browser settings.
                  </small>
                )}

              </div>


              <form
                className="text-query"
                onSubmit={
                  submitText
                }
              >
                <input
                  value={
                    question
                  }
                  onChange={(event) =>
                    setQuestion(
                      event.target
                        .value
                    )
                  }
                  placeholder="Or type your question here..."
                  disabled={
                    busy
                  }
                />

                <button
                  type="submit"
                  disabled={
                    busy ||
                    !question.trim()
                  }
                >
                  {busy ? (
                    <LoaderCircle
                      className="spin"
                      size={17}
                    />
                  ) : (
                    <Send
                      size={17}
                    />
                  )}
                </button>
              </form>


              {error && (
                <div className="error-box">
                  {error}
                </div>
              )}


              <div className="console-footer">

                <LatencyBadge
                  latency={
                    latency
                  }
                />

                <span className="privacy-note">
                  <ShieldCheck
                    size={14}
                  />
                  Audio is sent only
                  when you submit.
                </span>

              </div>

            </div>


            <div className="result-card glass">

              <div className="card-top">
                <div>
                  <div className="section-kicker">
                    RAG RESPONSE
                  </div>

                  <h2>
                    Grounded output.
                  </h2>
                </div>

                <ArrowUpRight
                  size={19}
                />
              </div>


              {busy && (
                <div className="loading-line">
                  <span />
                  <span />
                  <span />

                  <em>
                    {stage ===
                    "transcribing"
                      ? "Transcribing voice…"
                      : "Retrieving grounded answer…"}
                  </em>
                </div>
              )}


              <AnswerPanel
                answer={answer}
                sources={sources}
              />

            </div>

          </div>
        </section>


        <Pipeline />


        <section
          id="about"
          className="about-section container"
        >
          <div className="about-card">

            <div className="section-kicker">
              BRAHMA / VOICE RAG
            </div>

            <h2>
              Designed for measurable
              voice intelligence.
            </h2>

            <p>
              The frontend keeps the
              interaction simple while
              exposing microphone state,
              transcription, backend
              health, response latency
              and retrieved context.
            </p>

          </div>
        </section>

      </main>


      <footer className="footer container">
        <span>
          Built & Designed by Block Party
        </span>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <a
            href="https://www.instagram.com/vinitmishraaa/"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Instagram"
            title="Instagram"
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              textDecoration: "none",
            }}
          >
            <Instagram size={18} />
          </a>

          <a
            href="https://github.com/vinitmishraaa"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="GitHub"
            title="GitHub"
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              textDecoration: "none",
            }}
          >
            <Github size={18} />
          </a>
        </div>
      </footer>
    </div>
  );
}