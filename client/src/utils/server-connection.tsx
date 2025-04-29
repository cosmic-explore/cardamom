import { LOGIN, JOIN_MATCH, REFRESH_MATCH } from "../constants/server-endpoints"

const buildPostRequest = (body : string): RequestInit => {
    return {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body,
        credentials: 'include'
    }
}

const buildGetRequest = (): RequestInit => {
    return {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'GET',
        credentials: 'include'
    }
}

export const login = async (playerName: string) => {
    let requestBody = JSON.stringify({player_name: playerName})
    let response = await fetch(LOGIN, buildPostRequest(requestBody))
    return response.json()
}

export const joinMatch = async (): Promise<EventSource> => {
    return new EventSource(JOIN_MATCH, {withCredentials: true})
}

export const refreshMatch = async () => {
    /** Triggers a server sent event */
    await fetch(REFRESH_MATCH, buildGetRequest())
}