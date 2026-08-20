import React from "react";

import {
  FileText,
} from "lucide-react";


export default function SourceList({
  sources = [],
}) {
  if (!sources.length) {
    return null;
  }


  return (
    <section className="sources">

      <div className="section-kicker">
        RETRIEVED CONTEXT
      </div>


      <div className="source-list">

        {sources.map(
          (
            source,
            index
          ) => {

            const text =
              source.text ||
              "";

            const score =
              Number(
                source.score
              );

            return (
              <article
                className="source-card"
                key={`${source.query_id}-${source.content_lang}-${index}`}
              >

                <FileText
                  size={17}
                />

                <div>

                  <strong>
                    Source {index + 1}
                  </strong>

                  <p>
                    {text}
                  </p>

                  <small>
                    {Number.isFinite(
                      score
                    )
                      ? `relevance ${(score * 100).toFixed(0)}%`
                      : ""}

                    {source.content_lang
                      ? ` · ${source.content_lang}`
                      : ""}

                    {source.query_id
                      ? ` · query ${source.query_id}`
                      : ""}
                  </small>

                </div>

              </article>
            );
          }
        )}

      </div>

    </section>
  );
}