import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";


export function useMicrophone() {
  const [devices, setDevices] =
    useState([]);

  const [
    selectedDeviceId,
    setSelectedDeviceId,
  ] = useState("");

  const [permission, setPermission] =
    useState("unknown");

  const [recording, setRecording] =
    useState(false);

  const [elapsedMs, setElapsedMs] =
    useState(0);

  const [audioBlob, setAudioBlob] =
    useState(null);

  const [error, setError] =
    useState("");

  const recorderRef =
    useRef(null);

  const streamRef =
    useRef(null);

  const startedAtRef =
    useRef(0);

  const timerRef =
    useRef(null);

  const chunksRef =
    useRef([]);

  const stopResolverRef =
    useRef(null);


  const refreshDevices =
    useCallback(async () => {
      try {
        const list =
          await navigator.mediaDevices.enumerateDevices();

        const inputs =
          list.filter(
            (device) =>
              device.kind ===
              "audioinput"
          );

        setDevices(inputs);

        setSelectedDeviceId(
          (current) =>
            current ||
            inputs[0]?.deviceId ||
            ""
        );
      } catch (err) {
        setError(
          err.message ||
            "Could not enumerate microphones."
        );
      }
    }, []);


  useEffect(() => {
    refreshDevices();

    const handler =
      () => refreshDevices();

    navigator.mediaDevices?.addEventListener?.(
      "devicechange",
      handler
    );

    return () => {
      navigator.mediaDevices?.removeEventListener?.(
        "devicechange",
        handler
      );
    };
  }, [refreshDevices]);


  const start =
    useCallback(async () => {
      setError("");
      setAudioBlob(null);

      try {
        const constraints =
          selectedDeviceId
            ? {
                audio: {
                  deviceId: {
                    exact:
                      selectedDeviceId,
                  },
                  echoCancellation:
                    true,
                  noiseSuppression:
                    true,
                  autoGainControl:
                    true,
                },
              }
            : {
                audio: {
                  echoCancellation:
                    true,
                  noiseSuppression:
                    true,
                  autoGainControl:
                    true,
                },
              };

        const stream =
          await navigator.mediaDevices.getUserMedia(
            constraints
          );

        setPermission("granted");

        await refreshDevices();

        let mimeType =
          "audio/webm";

        if (
          !MediaRecorder.isTypeSupported(
            "audio/webm;codecs=opus"
          )
        ) {
          if (
            MediaRecorder.isTypeSupported(
              "audio/webm"
            )
          ) {
            mimeType =
              "audio/webm";
          } else {
            mimeType = "";
          }
        }

        const recorder =
          mimeType
            ? new MediaRecorder(
                stream,
                { mimeType }
              )
            : new MediaRecorder(
                stream
              );

        chunksRef.current = [];

        recorder.ondataavailable =
          (event) => {
            if (
              event.data &&
              event.data.size > 0
            ) {
              chunksRef.current.push(
                event.data
              );
            }
          };


        recorder.onstop = () => {
          const finalType =
            recorder.mimeType ||
            "audio/webm";

          const blob =
            new Blob(
              chunksRef.current,
              {
                type: finalType,
              }
            );

          setAudioBlob(blob);

          stream
            .getTracks()
            .forEach(
              (track) =>
                track.stop()
            );

          streamRef.current = null;

          if (
            stopResolverRef.current
          ) {
            stopResolverRef.current(
              blob
            );

            stopResolverRef.current =
              null;
          }
        };


        recorder.onerror =
          () => {
            const message =
              "Microphone recording failed.";

            setError(message);

            if (
              stopResolverRef.current
            ) {
              stopResolverRef.current(
                null
              );

              stopResolverRef.current =
                null;
            }
          };


        recorder.start();

        recorderRef.current =
          recorder;

        streamRef.current =
          stream;

        startedAtRef.current =
          performance.now();

        setElapsedMs(0);
        setRecording(true);

        timerRef.current =
          window.setInterval(
            () => {
              setElapsedMs(
                performance.now() -
                  startedAtRef.current
              );
            },
            50
          );
      } catch (err) {
        setPermission("denied");

        setError(
          err.message ||
            "Microphone permission was denied."
        );
      }
    }, [
      refreshDevices,
      selectedDeviceId,
    ]);


  const stop =
    useCallback(() => {
      return new Promise(
        (resolve) => {
          const recorder =
            recorderRef.current;

          if (
            !recorder ||
            recorder.state ===
              "inactive"
          ) {
            resolve(
              audioBlob || null
            );
            return;
          }

          stopResolverRef.current =
            resolve;

          recorder.stop();

          recorderRef.current =
            null;

          setRecording(false);

          window.clearInterval(
            timerRef.current
          );

          timerRef.current =
            null;
        }
      );
    }, [audioBlob]);


  useEffect(() => {
    return () => {
      window.clearInterval(
        timerRef.current
      );

      recorderRef.current?.stop();

      streamRef.current
        ?.getTracks()
        .forEach(
          (track) =>
            track.stop()
        );
    };
  }, []);


  return {
    devices,
    selectedDeviceId,
    setSelectedDeviceId,
    permission,
    recording,
    elapsedMs,
    audioBlob,
    error,
    start,
    stop,
    refreshDevices,
  };
}