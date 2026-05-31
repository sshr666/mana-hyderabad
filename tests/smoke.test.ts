import { describe, expect, it } from "vitest";

import { CATEGORY_LABELS, HYDERABAD_CENTER, MAP_STYLE_URL } from "../lib/map-config";

describe("frontend project configuration", () => {
  it("defines a Hyderabad-centered map configuration", () => {
    expect(HYDERABAD_CENTER.latitude).toBeCloseTo(17.385, 3);
    expect(HYDERABAD_CENTER.longitude).toBeCloseTo(78.4867, 3);
    expect(MAP_STYLE_URL).toContain("style.json");
  });

  it("has labels for the core complaint categories", () => {
    expect(CATEGORY_LABELS.SANITATION).toBe("Sanitation");
    expect(CATEGORY_LABELS.WATERLOGGING).toBe("Waterlogging");
    expect(CATEGORY_LABELS.OTHER).toBe("Other");
  });
});
