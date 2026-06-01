cube(`MarketingSpendCube`, {
  sql: `SELECT m.*, p.name FROM marketing_spend m JOIN properties p ON m.propertyid = p.id`,

  measures: {
    monthlySpend: {
      sql: `monthlyspend`,
      type: `sum`,
      description: `Active monthly advertising channel investment`
    }
  },

  dimensions: {
    propertyId: {
      sql: `propertyid`,
      type: `string`,
      primaryKey: true
    },
    name: {
      sql: `name`,
      type: `string`
    },
    channel: {
      sql: `channel`,
      type: `string`
    }
  }
});