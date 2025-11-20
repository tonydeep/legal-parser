import { pgTable, text, timestamp, boolean, jsonb, integer } from "drizzle-orm/pg-core"

// Better Auth tables
export const user = pgTable("user", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("email_verified").notNull().default(false),
  image: text("image"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
})

export const session = pgTable("session", {
  id: text("id").primaryKey(),
  expiresAt: timestamp("expires_at").notNull(),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
})

export const account = pgTable("account", {
  id: text("id").primaryKey(),
  accountId: text("account_id").notNull(),
  providerId: text("provider_id").notNull(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  accessToken: text("access_token"),
  refreshToken: text("refresh_token"),
  idToken: text("id_token"),
  expiresAt: timestamp("expires_at"),
  password: text("password"),
})

export const verification = pgTable("verification", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: timestamp("expires_at").notNull(),
})

// Legal Parser tables
export const document = pgTable("document", {
  id: text("id").primaryKey(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  title: text("title"),
  documentType: text("document_type"),
  documentNumber: text("document_number"),
  issueDate: timestamp("issue_date"),
  effectiveDate: timestamp("effective_date"),
  issuingAuthority: text("issuing_authority"),
  content: text("content"),
  parsedStructure: jsonb("parsed_structure"),
  urn: text("urn"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
})

export const parseHistory = pgTable("parse_history", {
  id: text("id").primaryKey(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  documentId: text("document_id").references(() => document.id, { onDelete: "set null" }),
  inputText: text("input_text"),
  outputCypher: text("output_cypher"),
  outputUrn: text("output_urn"),
  parseType: text("parse_type"), // 'basic' | 'enhanced'
  componentCount: integer("component_count"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
})

export const aiConversation = pgTable("ai_conversation", {
  id: text("id").primaryKey(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  documentId: text("document_id").references(() => document.id, { onDelete: "set null" }),
  messages: jsonb("messages").notNull().default([]),
  model: text("model"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
})

// Type exports
export type User = typeof user.$inferSelect
export type NewUser = typeof user.$inferInsert
export type Document = typeof document.$inferSelect
export type NewDocument = typeof document.$inferInsert
export type ParseHistory = typeof parseHistory.$inferSelect
export type AIConversation = typeof aiConversation.$inferSelect
