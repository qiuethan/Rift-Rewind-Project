import { analyticsApi, PerformanceAnalysisRequest, InsightRequest } from '@/api/analytics';

export const analyticsActions = {
  /**
   * Analyze match performance
   */
  analyzePerformance: async (data: PerformanceAnalysisRequest) => {
    try {
      const analysis = await analyticsApi.analyzePerformance(data);
      return { success: true, data: analysis };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to analyze performance',
      };
    }
  },

  /**
   * Generate AI insights
   */
  generateInsights: async (data: InsightRequest) => {
    try {
      const insights = await analyticsApi.generateInsights(data);
      return { success: true, data: insights };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to generate insights',
      };
    }
  },
};
