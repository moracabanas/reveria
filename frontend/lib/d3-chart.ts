import * as d3 from "d3";
import { ChartData, DataPoint } from "@/lib/chart-types";

interface RenderOptions {
  width: number;
  height: number;
  margin: { top: number; right: number; bottom: number; left: number };
}

export function renderChart(
  container: HTMLDivElement,
  data: ChartData,
  options: RenderOptions
): () => void {
  const { width, height, margin } = options;
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  d3.select(container).selectAll("*").remove();

  const svg = d3
    .select(container)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", `0 0 ${width} ${height}`);

  const g = svg
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const sampleRate = Math.ceil(data.historical.length / 5000);
  const sampledHistorical =
    data.historical.length > 5000
      ? data.historical.filter((_, i) => i % sampleRate === 0)
      : data.historical;

  const combinedData = [...sampledHistorical, ...data.prediction];

  if (combinedData.length === 0) return () => {};

  const xExtent = d3.extent(combinedData, (d) => d.index) as [number, number];
  const yExtent = d3.extent(combinedData, (d) => d.value) as [number, number];
  const yPadding = (yExtent[1] - yExtent[0]) * 0.1;

  const xScale = d3.scaleLinear().domain(xExtent).range([0, innerWidth]);
  const yScale = d3
    .scaleLinear()
    .domain([yExtent[0] - yPadding, yExtent[1] + yPadding])
    .range([innerHeight, 0]);

  g.append("defs")
    .append("clipPath")
    .attr("id", "chart-clip")
    .append("rect")
    .attr("width", innerWidth)
    .attr("height", innerHeight);

  const chartArea = g.append("g").attr("clip-path", "url(#chart-clip)");

  const line = d3
    .line<DataPoint>()
    .x((d) => xScale(d.index))
    .y((d) => yScale(d.value))
    .curve(d3.curveMonotoneX);

  if (sampledHistorical.length > 0) {
    chartArea
      .append("path")
      .datum(sampledHistorical)
      .attr("fill", "none")
      .attr("stroke", "#2563eb")
      .attr("stroke-width", 1.5)
      .attr("d", line);
  }

  if (data.prediction.length > 0) {
    const predictionData = sampledHistorical.length > 0
      ? [sampledHistorical[sampledHistorical.length - 1], ...data.prediction]
      : data.prediction;

    chartArea
      .append("path")
      .datum(predictionData)
      .attr("fill", "none")
      .attr("stroke", "#2563eb")
      .attr("stroke-width", 1.5)
      .attr("stroke-dasharray", "4,4")
      .attr("d", line);
  }

  const xAxis = d3.axisBottom(xScale).ticks(5);
  const yAxis = d3.axisLeft(yScale).ticks(5);

  g.append("g")
    .attr("transform", `translate(0,${innerHeight})`)
    .call(xAxis)
    .attr("class", "x-axis");

  g.append("g").call(yAxis).attr("class", "y-axis");

  g.append("g")
    .attr("class", "grid")
    .attr("opacity", 0.1)
    .call(d3.axisLeft(yScale).tickSize(-innerWidth).tickFormat(() => ""));

  if (data.metadata && data.metadata.original_length > data.metadata.window_size) {
    const infoText = `Showing last ${data.metadata.window_size.toLocaleString()} of ${data.metadata.original_length.toLocaleString()} points`;
    g.append("text")
      .attr("x", innerWidth)
      .attr("y", -margin.top / 2 + 5)
      .attr("text-anchor", "end")
      .attr("fill", "#6b7280")
      .attr("font-size", "11px")
      .text(infoText);
  }

  const zoom = d3
    .zoom<SVGSVGElement, unknown>()
    .scaleExtent([1, 50])
    .extent([
      [0, 0],
      [innerWidth, innerHeight],
    ])
    .on("zoom", (event) => {
      const newXScale = event.transform.rescaleX(xScale);
      g.select(".x-axis").call(d3.axisBottom(newXScale).ticks(5) as any);
      const zoomedLine = line.x((d: DataPoint) => newXScale(d.index));
      chartArea.selectAll("path").attr("d", zoomedLine as any);
    });

  svg.call(zoom as any);

  return () => {
    d3.select(container).selectAll("*").remove();
  };
}

export function clearChart(container: HTMLDivElement): void {
  d3.select(container).selectAll("*").remove();
}
