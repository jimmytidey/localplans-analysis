export enum FetchState {
  DEFAULT = "DEFAULT",
  LOADING = "LOADING",
  SUCCESS = "SUCCESS",
  ERROR = "ERROR",
}

export type PersonasData = {
  ltla_code: string;
  ltla_name: string;
  gender: string;
  ethnicity: string;
  age_category: number;
  notes: number;
  age: number;
  employment: string;
  observation: number;
  occupation: string;
  headshot_file: string;
  disability_status: string;
  percentage: string;
};

export type LtlaListData = {
  ltla_code: string;
  ltla_name: string;
};
