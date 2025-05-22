export type ActionData = {
    id: string;
    name: string;
    reach: string;
    power: number;
};

export type BoardData = {
    size_x: number;
    size_y: number;
    columns: PositionData[][];
};

export type CommandData = {
    creature: CreatureData;
    move_target: PositionData;
    action: ActionData;
    action_target: PositionData;
};

export type CreatureData = {
    id: string;
    species_id: string;
    player_id: string;
    nickname: string;
    level: number;
    max_hp: number;
    current_hp: number;
    attack: number;
    speed: number;
    actions: ActionData[];
};

export type MatchData = {
    id: string;
    board: BoardData;
    player_1: PlayerData | null;
    player_2: PlayerData | null;
    active: boolean;
};

export type PositionData = {
    x: number;
    y: number;
    creature: CreatureData;
};

export type PlayerData = {
    id: string;
    name: string;
    creatures: CreatureData[];
};
