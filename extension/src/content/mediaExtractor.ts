import type { MediaCandidate, MediaType } from "../shared/types";

const MIN_TEXT_LENGTH = 280;

export function extractMediaCandidates(root: ParentNode = document): MediaCandidate[] {
  const candidates: MediaCandidate[] = [];
  candidates.push(...extractImages(root));
  candidates.push(...extractVideos(root));
  candidates.push(...extractAudio(root));
  candidates.push(...extractTextBlocks(root));
  return candidates;
}

function extractImages(root: ParentNode): MediaCandidate[] {
  return Array.from(root.querySelectorAll("img"))
    .filter((element) => element.naturalWidth >= 96 && element.naturalHeight >= 96)
    .map((element) => ({
      id: assignCandidateId(element, "image"),
      mediaType: "image",
      sourceUrl: element.currentSrc || element.src,
      metadata: {
        alt: element.alt,
        naturalWidth: element.naturalWidth,
        naturalHeight: element.naturalHeight,
        renderedWidth: element.clientWidth,
        renderedHeight: element.clientHeight,
        loading: element.loading,
        crossOrigin: element.crossOrigin,
        pageUrl: document.location.href
      }
    }));
}

function extractVideos(root: ParentNode): MediaCandidate[] {
  return Array.from(root.querySelectorAll("video")).map((element) => ({
    id: assignCandidateId(element, "video"),
    mediaType: "video",
    sourceUrl: element.currentSrc || firstSource(element),
    metadata: {
      duration: Number.isFinite(element.duration) ? element.duration : 0,
      width: element.videoWidth,
      height: element.videoHeight,
      paused: element.paused,
      muted: element.muted,
      readyState: element.readyState,
      hasAudio: true,
      pageUrl: document.location.href
    }
  }));
}

function extractAudio(root: ParentNode): MediaCandidate[] {
  return Array.from(root.querySelectorAll("audio")).map((element) => ({
    id: assignCandidateId(element, "audio"),
    mediaType: "audio",
    sourceUrl: element.currentSrc || firstSource(element),
    metadata: {
      duration: Number.isFinite(element.duration) ? element.duration : 0,
      paused: element.paused,
      muted: element.muted,
      readyState: element.readyState,
      pageUrl: document.location.href
    }
  }));
}

function extractTextBlocks(root: ParentNode): MediaCandidate[] {
  const selectors = "article p, main p, [role='article'], blockquote, section p";
  return Array.from(root.querySelectorAll<HTMLElement>(selectors))
    .map((element) => ({
      element,
      text: normalizeText(element.innerText)
    }))
    .filter(({ text }) => text.length >= MIN_TEXT_LENGTH)
    .slice(0, 8)
    .map(({ element, text }) => ({
      id: assignCandidateId(element, "text"),
      mediaType: "text",
      content: text.slice(0, 6000),
      metadata: {
        tagName: element.tagName.toLowerCase(),
        textLength: text.length,
        pageTitle: document.title,
        pageUrl: document.location.href
      }
    }));
}

function assignCandidateId(element: Element, mediaType: MediaType): string {
  const existing = element.getAttribute("data-ghostproof-id");
  if (existing) {
    return existing;
  }
  const id = `gp_${mediaType}_${crypto.randomUUID()}`;
  element.setAttribute("data-ghostproof-id", id);
  return id;
}

function firstSource(element: HTMLMediaElement): string | undefined {
  const source = element.querySelector("source");
  return source?.src;
}

function normalizeText(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}
