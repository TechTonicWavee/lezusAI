// Global TypeScript Ambient Declarations for DRISHTI AI Frontend

declare module "react" {
  export = React;
  export as namespace React;
}

declare namespace React {
  export type ReactNode = any;
  export type ReactElement = any;
  export type ComponentType<P = {}> = any;
  export type FC<P = {}> = (props: P) => any;
  export function useState<T = any>(initialState?: T | (() => T)): [T, (newState: T | ((prev: T) => T)) => void];
  export function useEffect(effect: () => void | (() => void), deps?: readonly any[]): void;
  export function useRef<T = any>(initialValue?: T): { current: T };
  export function useMemo<T = any>(factory: () => T, deps: readonly any[] | undefined): T;
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: readonly any[]): T;
  export type FormEvent<T = any> = any;
  export type MouseEvent<T = any> = any;
  export type ChangeEvent<T = any> = any;
}

declare namespace JSX {
  interface Element extends React.ReactElement {}
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare namespace NodeJS {
  interface ProcessEnv {
    [key: string]: string | undefined;
    NEXT_PUBLIC_API_URL?: string;
  }
}

declare module "next" {
  export interface Metadata {
    title?: string;
    description?: string;
    [key: string]: any;
  }
}

