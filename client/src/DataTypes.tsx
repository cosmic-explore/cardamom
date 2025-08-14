export type ActionData = {
    id: string
    name: string
    reach: string
    power: number
}

export type BoardData = {
    size_x: number
    size_y: number
    columns: PositionData[][]
}

export type CommandData = {
    creature_state_id: string
    move_target: PositionData | null
    action: ActionData | null
    action_target: PositionData | null
}

export type CreatureData = {
    id: string
    species_id: string
    player_id: string
    nickname: string
    level: number
    max_hp: number
    attack: number
    speed: number
    actions: ActionData[]
}

export type CreatureState = {
    id: string
    creature_id: string
    current_hp: number
    position: PositionData
    creature: CreatureData
}

export type MatchData = {
    id: string
    board: BoardData
    history: [[{ board: BoardData; creature_states: CreatureState[] }]]
    player_1: PlayerData | null
    player_2: PlayerData | null
    creature_states: CreatureState[]
    active: boolean
    turn_number: number
}

export type PositionData = {
    x: number
    y: number
    creature_state_id: string | null
}

export type PlayerData = {
    id: string
    name: string
    creatures: CreatureData[]
}

export type PlayerMatches = {
    current: string
    finished: string[]
}
