// Global TypeScript Ambient Declarations for DRISHTI AI Frontend

declare global {
  namespace JSX {
    interface Element {
      type: any;
      props: any;
      key: any;
    }
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }

  namespace React {
    type ReactNode = any;
    type ReactElement<P = any, T extends string | any = any> = any;
    type ComponentType<P = {}> = any;
    type FC<P = {}> = (props: P) => any;
    function useState<T = any>(initialState?: T | (() => T)): [T, (newState: T | ((prev: T) => T)) => void];
    function useEffect(effect: () => void | (() => void), deps?: readonly any[]): void;
    function useRef<T = any>(initialValue?: T): { current: T };
    function useMemo<T = any>(factory: () => T, deps: readonly any[] | undefined): T;
    function useCallback<T extends (...args: any[]) => any>(callback: T, deps: readonly any[]): T;
    type FormEvent<T = any> = any;
    type MouseEvent<T = any> = any;
    type ChangeEvent<T = any> = any;
    
    namespace JSX {
      interface Element {
        type: any;
        props: any;
        key: any;
      }
      interface IntrinsicElements {
        [elemName: string]: any;
      }
    }
  }

  namespace NodeJS {
    interface ProcessEnv {
      [key: string]: string | undefined;
      NEXT_PUBLIC_API_URL?: string;
    }
  }
}

declare module "react" {
  export const useState: typeof React.useState;
  export const useEffect: typeof React.useEffect;
  export const useRef: typeof React.useRef;
  export const useMemo: typeof React.useMemo;
  export const useCallback: typeof React.useCallback;
  export type ReactNode = React.ReactNode;
  export type ReactElement = React.ReactElement;
  export type FC<P = {}> = React.FC<P>;
  export default React;
}

declare module "next" {
  export interface Metadata {
    title?: string;
    description?: string;
    [key: string]: any;
  }
}

export {};
