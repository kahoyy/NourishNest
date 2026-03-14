export interface InventoryTag {
  id: number
  name: string
}

export interface InventoryItem {
  id: number
  name: string
  quantity: number
  unit: string
  perishable: boolean
  expiry_date: string | null
  tags: InventoryTag[]
  created_at: string
  updated_at: string
}

export interface CreateInventoryItemPayload {
  name: string
  quantity: number
  unit: string
  perishable: boolean
  expiry_date?: string | null
  tag_ids?: number[]
}

export interface UpdateInventoryItemPayload extends Partial<CreateInventoryItemPayload> {}

export interface InventoryFilters {
  perishable?: boolean
  tags?: number[]
  expired?: boolean
  page?: number
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface InventoryHistory {
  id: number
  action: string
  item_name: string
  created_at: string
  is_undone: boolean
}
